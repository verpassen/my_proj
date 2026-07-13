import torch
from torch import nn
import numpy as np
import matplotlib.pyplot as plt
from pyDOE import lhs
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class PINN_net(nn.Module):
    def __init__(self,input_dim,mean_value,std_value,device):
        super(PINN_net, self).__init__()
        self.X_mean = torch.from_numpy(mean_value.astype(np.float32)).to(device)
        self.X_std = torch.from_numpy(std_value.astype(np.float32)).to(device)
        self.device = device
        self.layer_num = len(input_dim)
        print(self.layer_num)
        # Define your neural network architecture here
        self.base = nn.Sequential()
        for i in range(0,self.layer_num-2):
          print(f'i={i}')

          self.base.add_module(str(i)+"linear", nn.Linear(input_dim[i],input_dim[i+1]))
          self.base.add_module(str(i)+"Act", nn.Tanh())
        self.base.add_module(str(self.layer_num-1)+ "linear",nn.Linear(input_dim[self.layer_num-2],input_dim[self.layer_num-1]))

        self.Initial_param()

    def inner_norm(self,X):
      return (X-self.X_mean) / self.X_std

    def Initial_param(self):
      for name, param in self.base.named_parameters():
        if name.endswith('linear.weight'):
          nn.init.xavier_normal_(param)
        elif name.endswith('linear.bias'):
          nn.init.zeros_(param)
    def data_mse(self,x,y,u_true):
      predict_out = self.forward(x,y)
      u_predict = predict_out[:,0].reshape(-1,1)
      mse = torch.nn.MSELoss()
      return mse(u_predict, u_true) # For boundaries or known points

    def predict(self,x,y):
      predict_out = self.forward(x,y)
      u_predict = predict_out[:,0].reshape(-1,1)
      return u_predict

    def forward(self, x,y):
      X = torch.cat([x,y],1).requires_grad_(True).to(self.device)
      X_norm = self.inner_norm(X)
      predict = self.base(X_norm)
      return predict

    def equation_mse(self,x,y):
      predict_out = self.forward(x,y)
      u = predict_out[:,0].reshape(-1,1)
      u_x = torch.autograd.grad(u.sum(),x,create_graph=True)[0]
      u_y = torch.autograd.grad(u.sum(),y,create_graph=True)[0]
      u_xx = torch.autograd.grad(u_x.sum(),x,create_graph=True)[0]
      u_yy = torch.autograd.grad(u_y.sum(),y,create_graph=True)[0]
      # source term : customized f based on the problem
      f = -2*(torch.pi**2)*torch.sin(torch.pi*x)*torch.sin(torch.pi*y)
      residual = u_xx + u_yy - f
      mse = torch.nn.MSELoss()
      zeros = torch.zeros_like(residual)
      return mse(residual,zeros)


# Generate sample data points (replace with your actual data)
def generate_data(N_col=2000,N_b=200, domain_lb=np.array([0.,0.]),domain_ub=np.array([1.0,1.0])):
  # why need array should be float ?

  # Collocation points
  col_samples = lhs(2,N_col)
  X_col = col_samples*(domain_ub - domain_lb)+domain_lb
  x_col = torch.tensor(X_col[:,0:1],dtype=torch.float32,requires_grad=True).to(device)
  y_col = torch.tensor(X_col[:,1:2],dtype=torch.float32,requires_grad=True).to(device)

  # Boundary points: Uniform on edges, u_true=0 (homogeneous Dirichlet)
  N_b_per_edge = N_b // 4
  b_points = []
  u_b_true = []
  # Bottom (y=0)
  x_bottom = torch.linspace(0, 1, N_b_per_edge).unsqueeze(1).to(device)
  y_bottom = torch.zeros_like(x_bottom).to(device)
  b_points.append((x_bottom, y_bottom))
  u_b_true.append(torch.zeros_like(x_bottom))
  # Top (y=1)
  x_top = torch.linspace(0, 1, N_b_per_edge).unsqueeze(1).to(device)
  y_top = torch.ones_like(x_top).to(device)
  b_points.append((x_top, y_top))
  u_b_true.append(torch.zeros_like(x_top))
  # Left (x=0)
  x_left = torch.zeros(N_b_per_edge, 1).to(device)
  y_left = torch.linspace(0, 1, N_b_per_edge).unsqueeze(1).to(device)
  b_points.append((x_left, y_left))
  u_b_true.append(torch.zeros_like(y_left))
  # Right (x=1)
  x_right = torch.ones(N_b_per_edge, 1).to(device)
  y_right = torch.linspace(0, 1, N_b_per_edge).unsqueeze(1).to(device)
  b_points.append((x_right, y_right))
  u_b_true.append(torch.zeros_like(y_right))

  # concat all boundaries
  x_b = torch.cat([xp for xp,yp in b_points],dim=0)
  y_b = torch.cat([yp for xp,yp in b_points],dim=0)
  u_true_b = torch.cat(u_b_true, dim=0)
  return (x_col,y_col),(x_b,y_b, u_true_b)



def generate_interior_data(N_int=5000):
  int_samples = lhs(2,N_int)
  X_int = int_samples
  x_int = torch.tensor(X_int[:,0:1],dtype=torch.float32).to(device)
  y_int = torch.tensor(X_int[:,1:2],dtype=torch.float32).to(device)
  u_int_true = torch.sin(np.pi*x_int)*torch.sin(np.pi*y_int) # exact solution
  return x_int,y_int,u_int_true

def train_pinn(model, optimizer, num_epochs,alpha,interior_data=None):
  data_losses = []
  physic_losses = []
  total_losses = []

  for epoch in range(num_epochs):
    optimizer.zero_grad()
    # sample points
    (x_col,y_col),(x_b,y_b,u_true_b) = generate_data()

    # Calculate loss
    data_loss = model.data_mse(x_b,y_b,u_true_b)
    if interior_data:
      x_int,y_int ,u_int_true = interior_data
      data_loss+= model.data_mse(x_int,y_int,u_int_true)

    physic_loss = model.equation_mse(x_col,y_col)

    # Total loss
    total_loss = data_loss + alpha*physic_loss
    # Backward pass and update weights
    total_loss.backward()
    optimizer.step()
    # Log
    data_losses.append(data_loss.item())
    physic_losses.append(physic_loss.item())
    total_losses.append(total_loss.item())

    # Print training progress (optional)
    if (epoch + 1) % 100 == 0:
        print(f"Epoch [{epoch+1}/{num_epochs}],data loss:{data_loss.item():.6f},"
        f"Physic loss: {physic_loss.item():.6f}, Total Loss: {total_loss.item():.4f}")

  # visualization of the learning curve
  plt.figure(figsize=(15,4))
  plt.subplot(1,3,1)
  plt.semilogy(total_losses, label='Total')
  plt.semilogy(data_losses,label='Data')
  plt.semilogy(physic_losses,label='Physics')
  plt.xlabel('Epoch')
  plt.ylabel('Loss(log scale)')
  plt.title('Loss evolution')
  plt.grid(True)
  plt.subplot(1, 3, 2)
  x_test = torch.linspace(0, 1, 50).to(device)
  y_test = torch.linspace(0, 1, 50).to(device)
  xx, yy = torch.meshgrid(x_test , y_test, indexing='xy')
  # flatten for 2d field
  x_flat = xx.reshape(-1,1)
  y_flat = yy.reshape(-1,1)

  u_pred = model.predict(x_flat,y_flat).detach().cpu().numpy().reshape(50, 50)
  u_exact = (torch.sin(torch.pi * xx) * torch.sin(torch.pi * yy)).cpu().numpy()
  error = u_pred - u_exact
  plt.contourf(xx.cpu(), yy.cpu(),u_pred, levels=20, cmap='RdBu')
  plt.colorbar(label='Predict')
  plt.title('Prediction Result')
  plt.xlabel('x')
  plt.ylabel('y')

  plt.subplot(1, 3, 3)
  # Exact solution (broadcasts fine on 2D grid)
  plt.contourf(xx.cpu(), yy.cpu(), error, levels=20, cmap='RdBu')
  plt.colorbar(label='Error (Pred - Exact)')
  plt.title('Prediction Error')
  plt.xlabel('x')
  plt.ylabel('y')
  plt.tight_layout()
  return data_losses, physic_losses, total_losses

# Example usage
if __name__ == "__main__":
    # Define hyperparameters
    input_dim = [2,20,20,1]  # input layer 2, hidden layer : 20 + 20 , output layer 1
    num_epochs = 2000
    learning_rate = 0.001

    # Generate sample data (replace with your actual data)
    interior_data = generate_interior_data(500)
    # Create PINN model and optimizer
    model = PINN_net(input_dim,np.array([0.5,0.5]),np.array([0.5,0.5]),device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    # Train the PINN
    alpha = 2
    data_losses, physics_losses, total_losses = train_pinn(model, optimizer, num_epochs,alpha,interior_data)


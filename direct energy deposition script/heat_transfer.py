## DED Simulation by ai (not finished)
# 積分後溫度過高

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D
import scipy.special as sp
from scipy.integrate import solve_ivp
import time

class DEDSimulation:
    def __init__(self, domain_size=(10, 10, 5), grid_resolution=0.1):
        """
        Initialize DED simulation with domain size and grid resolution
        
        Parameters:
        -----------
        domain_size : tuple
            Size of the simulation domain in mm (x, y, z)
        grid_resolution : float
            Spatial resolution in mm
        """
        self.domain_size = domain_size
        self.resolution = grid_resolution
        
        # Create spatial grid
        self.x = np.arange(0, domain_size[0], grid_resolution)
        self.y = np.arange(0, domain_size[1], grid_resolution)
        self.z = np.arange(0, domain_size[2], grid_resolution)
        self.X, self.Y, self.Z = np.meshgrid(self.x, self.y, self.z, indexing='ij')
        
        # Initialize temperature field (ambient temperature in K)
        self.T_ambient = 300
        self.temperature = np.ones((len(self.x), len(self.y), len(self.z))) * self.T_ambient
        
        # Initialize material field (0: air, 1: solid substrate, 2: powder, 3: melt pool)
        self.material = np.zeros((len(self.x), len(self.y), len(self.z)))
        
        # Define substrate (bottom 1mm is solid)
        z_substrate = int(1.0 / grid_resolution)
        self.material[:, :, :z_substrate] = 1
        
        # Material properties
        self.properties = {
            'substrate': {
                'thermal_conductivity': 20,  # W/(m·K)
                'density': 7800,             # kg/m³
                'specific_heat': 500,        # J/(kg·K)
                'melting_point': 1700,       # K
                'latent_heat': 2.7e5         # J/kg
            },
            'powder': {
                'thermal_conductivity': 5,   # W/(m·K) - reduced due to porosity
                'density': 4500,             # kg/m³ - apparent density of powder
                'specific_heat': 500,        # J/(kg·K)
                'melting_point': 1700,       # K
                'latent_heat': 2.7e5         # J/kg
            }
        }
        
        # Process parameters
        self.laser = {
            'power': 500,                    # W
            'efficiency': 0.4,               # absorption efficiency
            'beam_radius': 0.8,              # mm
            'position': [5, 0, 5],           # mm, starting position
            'velocity': [0, 5, 0]            # mm/s, movement vector
        }
        
        self.powder = {
            'feed_rate': 0,                 # g/min
            'stream_radius': 2,              # mm at substrate
            'velocity': 20,                  # mm/s - particle velocity
            'size_mean': 0.05,               # mm - mean particle size
            'size_std': 0.02,                # mm - standard deviation
            'nozzle_position': [5, 0, 10],   # mm, starting position
            'nozzle_angle': 45               # degrees from vertical
        }
        
        # Time settings
        self.dt = 0.01                       # s
        self.time = 0                        # s
        self.history = {
            'time': [],
            'max_temp': [],
            'melt_pool_size': []
        }
        # defie the powder distribution
        self.powder['distribution'] = self._generate_powder_distribution()
       
    def _generate_powder_distribution(self, num_particles=10000):
        """Generate random powder particles with size distribution"""
        sizes = np.random.normal(self.powder['size_mean'], 
                                 self.powder['size_std'], 
                                 num_particles)
        # Ensure positive sizes
        sizes = np.abs(sizes)
        return sizes
    
    def update_laser_position(self, dt):
        """Update laser position based on velocity and time step"""
        self.laser['position'][0] += self.laser['velocity'][0] * dt
        self.laser['position'][1] += self.laser['velocity'][1] * dt
        self.laser['position'][2] += self.laser['velocity'][2] * dt
        
    def update_powder_nozzle_position(self, dt):
        """Update powder nozzle position to follow laser"""
        # In this simple model, nozzle follows the laser with fixed offset
        self.powder['nozzle_position'][0] = self.laser['position'][0]
        self.powder['nozzle_position'][1] = self.laser['position'][1]
        self.powder['nozzle_position'][2] = 10  # Fixed height
    
    def calculate_laser_heat_input(self):
        """Calculate heat input from laser using Gaussian distribution"""
        x_laser, y_laser, z_laser = self.laser['position']
        
        # Distance from each point to laser center (projected on surface)
        r_squared = ((self.X - x_laser)**2 + (self.Y - y_laser)**2)
        
        # Gaussian heat distribution
        intensity = self.laser['power'] * self.laser['efficiency'] / (np.pi * self.laser['beam_radius']**2)
        heat_flux = intensity * np.exp(-2 * r_squared / self.laser['beam_radius']**2)
        
        # Apply heat only to top surface or existing material
        heat_input = np.zeros_like(self.temperature)
        
        # Find the top surface at each (x,y) position
        for i in range(len(self.x)):
            for j in range(len(self.y)):
                r_squared =  (self.x[i] - x_laser)**2 + (self.y[j] - y_laser)**2
                point_heat_flux = intensity * np.exp(-2*r_squared/ self.laser['beam_radius']**2)
                # Find highest z with material
                for k in reversed(range(len(self.z))):
                    if self.material[i, j, k] > 0:
                        # Apply heat to this surface point 
                        heat_input[i, j, k] =  point_heat_flux
                        break
        
        return heat_input
    
    def deposit_powder(self, dt):
        """Simulate powder deposition from nozzle"""
        x_nozzle, y_nozzle, z_nozzle = self.powder['nozzle_position']
        
        # Calculate mass to deposit in this time step
        mass_rate = self.powder['feed_rate'] / 60  # convert to g/s
        mass_to_deposit = mass_rate * dt  # g
        
        # Calculate number of particles to deposit
        avg_particle_mass = (4/3) * np.pi * (self.powder['size_mean']/2)**3 * self.properties['powder']['density'] * 1e-6  # g
        num_particles = int(mass_to_deposit / avg_particle_mass)
        
        # For performance in this simulation, limit particles
        num_particles = min(num_particles, 100)
        
        # Generate particle positions in cone shape from nozzle
        angle_rad = np.radians(self.powder['nozzle_angle'])
        max_radius_at_substrate = self.powder['stream_radius']
        
        for _ in range(num_particles):
            # Random position within powder stream cone
            r = np.random.random() * max_radius_at_substrate
            theta = np.random.random() * 2 * np.pi
            
            # Calculate landing position
            x_offset = r * np.cos(theta)
            y_offset = r * np.sin(theta)
            
            x_land = x_nozzle + x_offset
            y_land = y_nozzle + y_offset
            
            # Convert to grid indices
            i = int(x_land / self.resolution)
            j = int(y_land / self.resolution)
            
            # Skip if outside domain
            if not (0 <= i < len(self.x) and 0 <= j < len(self.y)):
                continue
                
            # Find the first empty z position above existing material
            for k in range(len(self.z)):
                if k == len(self.z) - 1 or self.material[i, j, k] == 0 and self.material[i, j, k-1] > 0:
                    # Deposit powder here
                    self.material[i, j, k] = 2  # Set as powder
                    break
    
    def solve_heat_transfer(self, dt, heat_input):
        """Solve heat transfer equation using finite difference method"""
        # This is a simplified heat transfer solver
        # A more accurate solution would use proper 3D heat equation with phase change
        
        # Create copy of current temperature
        new_temp = np.copy(self.temperature)
        
        # Thermal diffusivity calculation (varies by material)
        alpha = np.zeros_like(self.temperature)
        for i in range(len(self.x)):
            for j in range(len(self.y)):
                for k in range(len(self.z)):
                    if self.material[i, j, k] == 0:  # Air
                        alpha[i, j, k] = 2.2e-5  # m²/s
                    elif self.material[i, j, k] == 1:  # Substrate
                        k_thermal = self.properties['substrate']['thermal_conductivity']
                        rho = self.properties['substrate']['density']
                        cp = self.properties['substrate']['specific_heat']
                        alpha[i, j, k] = k_thermal / (rho * cp) * 1e6  # mm²/s
                    else:  # Powder or melt
                        k_thermal = self.properties['powder']['thermal_conductivity']
                        rho = self.properties['powder']['density']
                        cp = self.properties['powder']['specific_heat']
                        alpha[i, j, k] = k_thermal / (rho * cp) * 1e6  # mm²/s
        
        # Apply explicit finite difference for heat diffusion
        # (This is a simplified version and not numerically stable for all dt values)
        dx = dy = dz = self.resolution
        
        # Apply boundary conditions and calculate new temperatures
        for i in range(1, len(self.x)-1):
            for j in range(1, len(self.y)-1):
                for k in range(1, len(self.z)-1):
                    if self.material[i, j, k] > 0:  # Only for material points
                        # Laplacian term (∇²T)
                        laplacian = (
                            (self.temperature[i+1, j, k] - 2*self.temperature[i, j, k] + self.temperature[i-1, j, k]) / dx**2 +
                            (self.temperature[i, j+1, k] - 2*self.temperature[i, j, k] + self.temperature[i, j-1, k]) / dy**2 +
                            (self.temperature[i, j, k+1] - 2*self.temperature[i, j, k] + self.temperature[i, j, k-1]) / dz**2
                        )
                        
                        # Heat equation: dT/dt = α∇²T + q
                        new_temp[i, j, k] = self.temperature[i, j, k] + dt * (
                            alpha[i, j, k] * laplacian + heat_input[i, j, k]
                        )
                        
                        # Check phase change (solid/powder to melt)
                        if (self.material[i, j, k] == 1 or self.material[i, j, k] == 2) and \
                           new_temp[i, j, k] > self.properties['substrate']['melting_point']:
                            self.material[i, j, k] = 3  # Set as melt pool
                        
                        # Simplified cooling and solidification
                        if self.material[i, j, k] == 3 and \
                           new_temp[i, j, k] < self.properties['substrate']['melting_point']:
                            self.material[i, j, k] = 1  # Solidify to solid
        
        # Apply constant temperature boundary at bottom
        new_temp[:, :, 0] = self.T_ambient
        
        # Convective cooling at top surface
        h_conv = 50  # W/(m²·K), convective heat transfer coefficient
        for i in range(len(self.x)):
            for j in range(len(self.y)):
                # Find top surface
                for k in reversed(range(len(self.z))):
                    if self.material[i, j, k] > 0:
                        # Apply convective cooling
                        q_conv = h_conv * (self.T_ambient - self.temperature[i, j, k]) * 1e-6  # Convert to mm scale
                        new_temp[i, j, k] += dt * q_conv
                        break
        
        self.temperature = new_temp
    
    def update(self, dt):
        """Update simulation by one time step"""
        # Update positions
        self.update_laser_position(dt)
        self.update_powder_nozzle_position(dt)
        
        # Calculate heat input
        heat_input = self.calculate_laser_heat_input()
        
        # Deposit powder
        self.deposit_powder(dt)
        
        # Solve heat transfer
        self.solve_heat_transfer(dt, heat_input)
        
        # Update time
        self.time += dt
        
        # Record history
        self.history['time'].append(self.time)
        self.history['max_temp'].append(np.max(self.temperature))
        self.history['melt_pool_size'].append(np.sum(self.material == 3))
    
    def run_simulation(self, total_time=1.0):
        """Run simulation for specified time"""
        steps = int(total_time / self.dt)
        for _ in range(steps):
            self.update(self.dt)
            # Optional: print progress
            if _ % 10 == 0:
                print(f"Time: {self.time:.3f}s, Max temp: {np.max(self.temperature):.2e}K")
    
    def visualize_results(self):
        """Visualize the current state of the simulation"""
        # Create 3D figure
        fig = plt.figure(figsize=(15, 10))
        
        # Plot 3D material
        ax1 = fig.add_subplot(221, projection='3d')
        ax1.set_title("Material Distribution")
        
        # Plot substrate (solid)
        substrate_points = np.where(self.material == 1)
        ax1.scatter(self.X[substrate_points], self.Y[substrate_points], self.Z[substrate_points], 
                   c='gray', marker='s', alpha=0.3, label='Substrate')
        
        # Plot powder
        powder_points = np.where(self.material == 2)
        ax1.scatter(self.X[powder_points], self.Y[powder_points], self.Z[powder_points], 
                   c='blue', marker='o', alpha=0.5, label='Powder')
        
        # Plot melt pool
        melt_points = np.where(self.material == 3)
        ax1.scatter(self.X[melt_points], self.Y[melt_points], self.Z[melt_points], 
                   c='red', marker='o', alpha=0.8, label='Melt Pool')
        
        # Plot laser position
        ax1.scatter(*self.laser['position'], c='yellow', marker='*', s=100, label='Laser')
        
        ax1.set_xlabel('X [mm]')
        ax1.set_ylabel('Y [mm]')
        ax1.set_zlabel('Z [mm]')
        ax1.legend()
        
        # Plot temperature at middle z cross-section
        ax2 = fig.add_subplot(222)
        mid_z = len(self.z) // 2
        cs = ax2.contourf(self.X[:, :, mid_z], self.Y[:, :, mid_z], self.temperature[:, :, mid_z],
                         levels=20, cmap='hot')
        plt.colorbar(cs, ax=ax2, label='Temperature [K]')
        ax2.set_title(f"Temperature at Z={self.z[mid_z]:.1f}mm")
        ax2.set_xlabel('X [mm]')
        ax2.set_ylabel('Y [mm]')
        
        # Plot temperature history
        ax3 = fig.add_subplot(223)
        ax3.plot(self.history['time'], self.history['max_temp'])
        ax3.set_xlabel('Time [s]')
        ax3.set_ylabel('Maximum Temperature [K]')
        ax3.set_title('Temperature History')
        ax3.grid(True)
        
        # Plot melt pool size history
        ax4 = fig.add_subplot(224)
        ax4.plot(self.history['time'], self.history['melt_pool_size'])
        ax4.set_xlabel('Time [s]')
        ax4.set_ylabel('Melt Pool Size [voxels]')
        ax4.set_title('Melt Pool Size History')
        ax4.grid(True)
        
        plt.tight_layout()
        plt.show()

    def create_animation(self, times=None):
        """Create an animation of the simulation over time"""
        # This is a placeholder for animation functionality
        # Would require storing state history at each time step
        pass


# Example usage
if __name__ == "__main__":
    # Create simulation instance
    sim = DEDSimulation(domain_size=(10, 20, 5), grid_resolution=0.2)
    
    # Set specific process parameters
    sim.laser['power'] = 300  # W
    sim.laser['velocity'] = [0, 3, 5]  # mm/s
    sim.powder['feed_rate'] = 8  # g/min
    
    # Run simulation
    print("Running simulation...")
    sim.run_simulation(total_time=2.0)
    
    # Visualize results
    sim.visualize_results()

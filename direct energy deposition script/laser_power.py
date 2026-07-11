# Laser Power simulation 
import numpy as np 
from matplotlib import cm 
import matplotlib.pyplot as plt 
from math import pi, exp, sqrt , sin, cos

def my_power(x,y,r0,P):
    # laser power distribution
    # P : laser power 
    # r : powder flow radius
    # lamb : wave length : 1064 nm 
    lamb = 1064*10**-6
    r = r0*sqrt(1+(lamb/pi/r0**2)**2)
    n = 2*P/(pi*r**2)*exp(-2*(x**2 + y**2)/r**2)
    return n 

def my_plane(x,y,n):
    # x, y are the mesh grid points 
    # n is the list [nx,ny,nz]
    # z = n[0]*x + n[1]*y + n[2]
    return n[0]*x + n[1]*y + n[2] 


def myIntensity(z):
    # 隨著 Z軸位置，光束的半徑變化狀況 
    w0 = 0.7 # 光束腰寬 mm
    lamb = 1064*10**-6 # 波長 1064 nm > mm
    I = w0 * sqrt(1+(lamb*z/pi/w0**2)**2) # laser power intensity 
    return I 

S = np.arange(-3,3,0.01)
Intensity = [myIntensity(z) for z in S]

fig1 = plt.figure()
ax1 = fig1.add_subplot(111)
ax1.plot(S,Intensity)
ax1.set_xlabel('Z Pos[mm]')
ax1.set_ylabel('Radius of the Laser beam[mm]')

x = np.arange(-3,3,0.05) # x location 
y = np.arange(-3,3,0.05) # y location
XX, YY = np.meshgrid(x,y) 
r0 = 2 # diameter of the powder stream
P = 300 # Laser Power [w]
 
#----
s1 = [0,0,10] # usign the normal vector define the section plane 
  
Z = np.ones_like(XX)
Z2 = np.ones_like(XX)
 
for i in range(len(XX)):
    for j in range(len(XX[0])):
        Z[i][j] = my_power(XX[i][j],YY[i][j],r0,P)
        Z2[i][j] = my_plane(XX[i][j],YY[i][j],s1)
        
Inter_pt = np.abs(Z-Z2) < 0.1
''' 
fig2 = plt.figure()
ax2 = fig2.add_subplot(111,projection="3d")
surf = ax2.plot_wireframe(XX,YY,Z,rstride = 10, cstride=10)
surf2 = ax2.plot_wireframe(XX,YY,Z2,rstride=20,cstride=20)
 
ax2.set_xlabel('x')
ax2.set_ylabel('y')
ax2.set_zlabel('z')
 
ax2.scatter(XX[Inter_pt],YY[Inter_pt],Z2[Inter_pt],c='red')
'''

ax3 = plt.figure().add_subplot(projection='3d')
ax3.plot_surface(XX,YY,Z ,edgecolor='royalblue', lw=0.5, rstride=8, cstride=8, alpha=0.3)

ax3.contourf(XX,YY,Z, zdir='z',offset=5,cmap='coolwarm')
ax3.contourf(XX,YY,Z, zdir='y',offset=3,cmap='coolwarm')

plt.show()



 

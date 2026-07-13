# 2026.July.13th review 
# need to review . find out which part is correct. 
# and integrate them into one script 
'''
import numpy as np
import matplotlib.pyplot as plt
from numpy import sin, cos, sqrt, tan, exp, pi
from scipy.integrate import dblquad

# Parameters
feed_rate = 10  # g/min
nozzle_angle = 30 * pi / 180  # rad
divergence_angle = 7 * pi / 180  # rad
scan_speed = 50  # m/min
x0 = 0  # mm, nozzle offset
nozzle_diameter = 1  # mm
working_distance = 10  # mm
sigma_init = 3.0  # initial standard deviation
N = 256  # grid points

# Grid
x = np.linspace(-20, 20, N)
y = np.linspace(-20, 20, N)
xx, yy = np.meshgrid(x, y)

def powder_dia(x, y, z=6):
    """Calculate powder jet diameter and radial distribution."""
    sigma = sigma_init + z * tan(divergence_angle)
    rp = 1 / (sigma * sqrt(2 * pi)) * exp(-0.5 * (x / sigma)**2)
    return sigma, rp

def calc_flux(x, y, num_tips=4):
    """Calculate powder flux for a multi-tip nozzle."""
    dev, _ = powder_dia(x, y)
    flux = np.zeros_like(x)
    angles = np.linspace(0, 2 * pi, num_tips, endpoint=False)
    for theta in angles:
        x_t = (x + x0) * cos(nozzle_angle + theta) - y * sin(nozzle_angle + theta)
        y_t = -(x + x0) * sin(nozzle_angle + theta) + y * cos(nozzle_angle + theta)
        flux += feed_rate / (num_tips * pi * dev**2) * exp(-0.5 * (x_t**2 + y_t**2) / dev**2)
    return flux

def check_mass_conservation():
    flux_func = lambda x, y: calc_flux(x, y)
    total_flux, _ = dblquad(flux_func, -3, 3, -3, 3)
    print(f"Integrated flux: {total_flux/60:.2f} g/s (Expected: {feed_rate/60:.2f} g/s)")

check_mass_conservation()

# Plot
fig, ax = plt.subplots()
powder_flux = calc_flux(xx, yy)
contour = ax.contourf(xx, yy, powder_flux, levels=50, cmap='viridis')
plt.colorbar(contour, label='Powder Flux (g/min/mm²)')
ax.set_xlabel('X (mm)')
ax.set_ylabel('Y (mm)')
ax.set_aspect('equal')
ax.set_ylim(-15,15)
ax.set_xlim(-15,15)
plt.title('Powder Flux Distribution (4-Tip Nozzle)')
plt.show()

'''

# 2024.May.12
import numpy as np  
# matplotlib.use('TkAgg',force=True)
import matplotlib.pyplot as plt 
from matplotlib.animation import FuncAnimation
from numpy import sin, cos, sqrt ,tan,exp, pi

# init configuration 
F = 50 # g/min , powder feed rate 
ang = 45*pi/180 # rad , angle of the nozzle 
the_disp = 4.2*pi/180 # rad ,powder divergence angle 
V = 50 # scan speed [m/min]

x0 = 8 # mm
d = 1 # nozzle tip hole diameter
r0 = 3 # diameter of the powder beam
N = 2**8
h = 10 # working distance
sigma_init = 1.5 # standard deviation 
#---
x = np.linspace(-10,10,N) # x location 
z = np.linspace(-d,d,N) # z location
y = np.linspace(0,15,N) # y location

def powder_dia(x,y):
    sigma = sigma_init + y*tan(the_disp) 
    rp = 1/sigma*sqrt(2*pi)*exp(-0.5*(d/sigma)**2)
    return sigma

def calc_flux(x,y):
    rp = powder_dia(x,y)
    x_t, y_t = (x+x0)*cos(ang) - y*sin(ang) ,  -(x+x0)*sin(ang) + y*cos(ang)  
    x_t2 ,y_t2 = -(x-x0)*sin(ang) - y*cos(ang)  ,-(x-x0)*cos(ang) - y*sin(ang)  
    flux = 0.5*F/(pi*rp**2)*(exp(-0.5*(y_t**2+x_t**2)/rp**2)+exp(-0.5*(y_t2**2+x_t2**2)/rp**2))
 
    return flux 

fig, ax = plt.subplots()
xx,yy = np.meshgrid(x,y)
pow_f = calc_flux(xx,yy)
ax.contourf(xx,yy,pow_f)
ax.set_xlabel(u'x')
ax.set_ylabel(u'y')
ax.set_aspect('auto')
ax.set_ylim(12,0)
ax.axis('equal') 
# ax.contour(xx,yy,flux)
#----

plt.show()


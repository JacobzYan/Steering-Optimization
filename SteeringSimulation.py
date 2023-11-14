# Simulation Function
# Takes in geometry object and outputs matched numerical vectors of objects

from SteeringGeometry import SteeringGeometry as str
import numpy as np


# Returns an error value for given geometry
# Inputs: geom -> Steering Geometry object, num_fit_points -> The length of the output vectors
# Outputs: a vector of inner wheel angles, a vector of outer wheel angles, a vector of ideal outer wheel angles
def sim(geom: str, num_fit_points: int):
    
    # Determine Phi
    geom.phi = theta2(geom.rack_spacing, geom.wt, geom.l_tierod, geom.l_str_arm, 0)

    # Determine rack vectors for inside and outside wheels
    x_i = np.linspace(0, -geom.x_travel, num_fit_points)
    x_o = np.linspace(0, geom.x_travel, num_fit_points)

    # Determine corresponding theta 2 lists
    theta2_i = theta2(geom.rack_spacing, geom.wt, geom.l_tierod, geom.l_str_arm, x_i)
    theta2_o = theta2(geom.rack_spacing, geom.wt, geom.l_tierod, geom.l_str_arm, x_o)
    
    # Determine corresponding theta_i and theta_o
    theta_i = np.pi - wheel_angle(theta2_i, geom.phi)
    theta_o = wheel_angle(theta2_o, geom.phi)

    # Determine ideal theta_o
    theta_o_ideal = theta_o_ideal_eq(geom.wb, geom.wt, theta_i)

    return theta_i, theta_o, theta_o_ideal


## Helper Functions
def theta2(a, wt, l1, l2, x):

    # Define initial variables
    d = (a**2 + (wt-x)**2)**0.5
    theta11 = np.arctan(a/(wt-x))
    theta12 = np.arccos((d**2 + l1**2 - l2**2) / (2*d*l1))
    theta1 = theta11 - theta12
    print(f'x: {x}')
    print(f'theta11: {theta11}')
    print(f'theta12: {theta12}')
    # Calculate theta2
    theta2 = np.arctan((a - l1*np.sin(theta1)) / (wt - x - l1*np.cos(theta1)))
    
    return theta2


def wheel_angle(theta2, phi):
    return theta2 + np.pi/2 - phi


def theta_o_ideal_eq(wb, wt, theta_i):
    return np.pi/2 - np.arctan((wb) / (wb/np.tan(np.pi/2-theta_i) + 2*wt))


# Example use
a = str()
print(a)
b = sim(a, 5)
print(f'x: {np.linspace(0, a.x_travel, 5)}')
print(f'output of sim:\n{b}')
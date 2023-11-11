# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 19:13:16 2023

Author: Tristan Houy

Copyright: Fri Nov 10 19:13:16 2023, Tristan Houy, All rights reserved.
"""

from numba import jit, prange
import numpy as np

# Constants
wb = 1500 # Wheelbase [mm]
x_travel = 30 # Steering rack travel [mm]
w_track = 800 # Track width [mm]
l_rack = 300 # Steering rack length [mm]

# Dependent Variables
wt = (w_track - l_rack)/2 # Equivalent steering thickness [mm]

# Variables
#rack_spacing = 200 # Front/back distance between steering rack axis and control arm bearing mounting
#l_tierod = 250 # Tierod length [mm]
#l_str_arm = 100 # distance from control arm mounts to steering arm mount [mm]
#phi = 11*np.pi/180 # Steering Arm offset angle [deg]
@jit(nopython=True,parallel=True) 
def cartesian_product_on_the_fly_mm(num_of_step,num_fit_points):
    rack_spacing=np.linspace(800, 900, num_of_step)
    l_tierod=np.linspace(600, 700, num_of_step)
    l_str_arm=np.linspace(400, 500, num_of_step)
    phi=np.linspace(-np.pi, np.pi, num_of_step) 
    
    results = []
    
    for i in prange(rack_spacing.size):
        for j in prange(l_tierod.size):
            for k in prange(l_str_arm.size):
                for l in prange(phi.size):
                    current_rack_spacing = rack_spacing[i]
                    current_l_tierod = l_tierod[j]
                    current_l_str_arm = l_str_arm[k]
                    current_phi = phi[l]

                    result = sim(current_rack_spacing, wt, current_l_tierod, current_l_str_arm, wb, x_travel, current_phi, num_fit_points)
                    results.append(result)
    return results
                
# Simulation Function
# Takes in geometry object and outputs matched numerical vectors of objects

# Returns an error value for given geometry
# Inputs: geom -> Steering Geometry object, num_fit_points -> The length of the output vectors
# Outputs: a vector of inner wheel angles, a vector of outer wheel angles, a vector of ideal outer wheel angles
@jit(nopython=True, parallel=True)
def sim(rack_spacing, wt, l_tierod, l_str_arm, wb, x_travel, phi, num_fit_points):
    
    # Determine Phi
    phi = theta2(rack_spacing, wt, l_tierod, l_str_arm, 0)

    # Determine rack vectors for inside and outside wheels
    x_i = np.linspace(0, x_travel, num_fit_points)
    x_o = np.linspace(0, -x_travel, num_fit_points)

    # Determine corresponding theta 2 lists
    theta2_i = theta2(rack_spacing, wt, l_tierod, l_str_arm, x_i)
    theta2_o = theta2(rack_spacing, wt, l_tierod, l_str_arm, x_o)
    
    # Determine corresponding theta_i and theta_o
    theta_i = wheel_angle(theta2_i, phi)
    theta_o = wheel_angle(theta2_o, phi)

    # Determine ideal theta_o
    theta_o_ideal = theta_o_ideal_eq(wb, wt, theta_i)

    return theta_i, theta_o, theta_o_ideal

# Helper Functions
# Jit has not found a way to parallelize this
@jit(nopython=True, parallel=False)
def theta2(a, wt, l1, l2, x):

    # Define initial variables
    d = np.sqrt(a**2 + (wt-x)**2)
    theta11 = np.arctan(a/(wt-x))
    theta12 = np.arccos((d**2 + l1**2 - l2**2) / (2*d*l1))
    theta1 = theta11 - theta12

    # Calculate theta2
    theta2 = np.arctan((a - l1*np.sin(theta1)) / (wt - x - l1*np.cos(theta1)))
    return theta2

@jit(nopython=True, parallel=True)
def wheel_angle(theta2, phi):
    return theta2 + np.pi/2 - phi

@jit(nopython=True, parallel=True)
def theta_o_ideal_eq(wb, wt, theta_i):
    return np.arctan((wb) / (wb/np.tan(theta_i) + 2*wt))

# Running the simulation
num_steps = 2 # Define the number of steps
num_fit_points = 100
simulation_results = cartesian_product_on_the_fly_mm(num_steps,num_fit_points)

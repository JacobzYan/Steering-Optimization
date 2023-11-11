# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 20:03:07 2023

Author: Tristan Houy

Copyright: Fri Nov 10 20:03:07 2023, Tristan Houy, All rights reserved.
"""

from numba import jit, prange
import numpy as np

# Simulation parameters
num_steps = 101 # Define the number of steps
num_fit_points = 100 # Define granularity

# Constants
wb = 1500 # Wheelbase [mm]
x_travel = 30 # Steering rack travel [mm]
w_track = 800 # Track width [mm]
l_rack = 300 # Steering rack length [mm]

# Dependent Variables
wt = (w_track - l_rack)/2 # Equivalent steering thickness [mm]

# Variables
rack_spacing_lower =  100 # Front/back distance between steering rack axis and control arm bearing mounting [mm]
rack_spacing_upper =  300

l_tierod_lower = 150 # Tierod length [mm]
l_tierod_upper = 350

l_str_arm_lower = 1 # Distance from control arm mounts to steering arm mount [mm]
l_str_arm_upper = 201

@jit(nopython=True,parallel=False) 
def cartesian_product_on_the_fly_mm(num_of_step,num_fit_points):
    rack_spacing=np.linspace(rack_spacing_lower, rack_spacing_upper, num_of_step)
    l_tierod=np.linspace(l_tierod_lower, l_tierod_upper, num_of_step)
    l_str_arm=np.linspace(l_str_arm_lower, l_str_arm_upper, num_of_step)
    
    results = []
    
    for i in prange(rack_spacing.size):
        for j in prange(l_tierod.size):
            for k in prange(l_str_arm.size):
                current_rack_spacing = rack_spacing[i]
                current_l_tierod = l_tierod[j]
                current_l_str_arm = l_str_arm[k]

                result = sim(current_rack_spacing, wt, current_l_tierod, current_l_str_arm, wb, x_travel, num_fit_points)
                results.append(result)
    return results
                
# Simulation Function
# Takes in geometry object and outputs matched numerical vectors of objects

# Returns an error value for given geometry
# Inputs: Steering geometry values and num_fit_points (the length of the output vectors)
# Outputs: A vector of inner wheel angles, a vector of outer wheel angles, a vector of ideal outer wheel angles
@jit(nopython=True, parallel=True)
def sim(rack_spacing, wt, l_tierod, l_str_arm, wb, x_travel, num_fit_points):
    
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

    # Preallocate results array
    results = np.empty((3, num_fit_points), dtype=np.float64)

    # Assign the results directly
    results[0, :] = theta_i
    results[1, :] = theta_o
    results[2, :] = theta_o_ideal

    return results

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

# Error calculation
@jit(nopython=True,parallel=True)
def RMSE(y_actual_np_vector,y_predicted_np_vector):
    
    #squared differences
    squared_differences=(y_actual_np_vector-y_predicted_np_vector)**2
    
    #square root mean of the squared errors/differences (RMSE)
    rmse=np.sqrt(np.mean(squared_differences))
    
    return rmse

# Running the simulation
simulation_results = cartesian_product_on_the_fly_mm(num_steps,num_fit_points)

# Running the error calculation
# Initialize a list to store RMSE results
rmse_results = []

# Iterate through each result in simulation_results
for result in simulation_results:
    # Extract the second row (actual values)
    y_actual_np_vector = result[1, :]
    
    # Extract the third row (predicted values)
    y_predicted_np_vector = result[2, :]

    # Calculate RMSE and append to the rmse_results list
    rmse = RMSE(y_actual_np_vector, y_predicted_np_vector)
    rmse_results.append(rmse)

# rmse_results now contains the RMSE for each simulation result

# Finding the minimum value in the RMSE list
min_rmse = min(rmse_results)
min_rmse_index = rmse_results.index(min_rmse)

print("Minimum RMSE:", min_rmse, "at index", min_rmse_index)


# Optimal Geometry
# The total number of combinations
total_combinations = num_steps ** 3

# Calculate the index in each dimension
index_rack_spacing = (min_rmse_index // (num_steps ** 2)) % num_steps
index_l_tierod = (min_rmse_index // num_steps) % num_steps
index_l_str_arm = min_rmse_index % num_steps

# Generate the arrays for variables
rack_spacing_array = np.linspace(rack_spacing_lower, rack_spacing_upper, num_steps)
l_tierod_array = np.linspace(l_tierod_lower, l_tierod_upper, num_steps)
l_str_arm_array = np.linspace(l_str_arm_lower, l_str_arm_upper, num_steps)

# Retrieve the optimal values
optimal_rack_spacing = rack_spacing_array[index_rack_spacing]
optimal_l_tierod = l_tierod_array[index_l_tierod]
optimal_l_str_arm = l_str_arm_array[index_l_str_arm]

print("Optimal Geometry:")
print("Rack Spacing:", optimal_rack_spacing)
print("Tierod Length:", optimal_l_tierod)
print("Steering Arm Length:", optimal_l_str_arm)

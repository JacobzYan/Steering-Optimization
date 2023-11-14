# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 20:03:07 2023

Author: Tristan Houy

Copyright: Fri Nov 10 20:03:07 2023, Tristan Houy, All rights reserved.
"""

from numba import jit, prange
import numpy as np

#def everything():
# Simulation parameters
num_steps = 10 # Define the number of steps
num_fit_points = 100 # Define granularity

# Constants
phi_lower_bound = np.radians(-15) # Lower bound for phi in radians [Deg] -> [Rad]
wb = 1500 # Wheelbase [mm]
x_travel = 30 # Steering rack travel [mm]
w_track = 800 # Track width [mm]
l_rack = 300 # Steering rack length [mm]

# Dependent Variables
wt = (w_track - l_rack)/2 # Equivalent steering thickness [mm]

# Variables
rack_spacing_lower =  50 # Front/back distance between steering rack axis and control arm bearing mounting [mm]
rack_spacing_upper =  450

l_tierod_lower = 50 # Tierod length [mm]
l_tierod_upper = 350

l_str_arm_lower = 50.1 # Distance from control arm mounts to steering arm mount [mm]
l_str_arm_upper = 350

rack_spacing=np.linspace(rack_spacing_lower, rack_spacing_upper, num_steps)
l_tierod=np.linspace(l_tierod_lower, l_tierod_upper, num_steps)
l_str_arm=np.linspace(l_str_arm_lower, l_str_arm_upper, num_steps)

@jit(nopython=True,parallel=False) 
def cartesian_product_on_the_fly_mm(num_fit_points, rack_spacing, l_tierod, l_str_arm):
    results = []
    
    for i in prange(rack_spacing.size):
        for j in prange(l_tierod.size):
            for k in prange(l_str_arm.size):
                current_rack_spacing = rack_spacing[i]
                current_l_tierod = l_tierod[j]
                current_l_str_arm = l_str_arm[k]
                
                result = sim(current_rack_spacing, wt, current_l_tierod, current_l_str_arm, wb, x_travel, num_fit_points, phi_lower_bound)
                results.append(result)
                
    return results
                
# Simulation Function
# Takes in geometry object and outputs matched numerical vectors of objects

# Returns an error value for given geometry
# Inputs: Steering geometry values and num_fit_points (the length of the output vectors)
# Outputs: A vector of inner wheel angles, a vector of outer wheel angles, a vector of ideal outer wheel angles
@jit(nopython=True, parallel=True)
def sim(rack_spacing, wt, l_tierod, l_str_arm, wb, x_travel, num_fit_points, phi_lower_bound):
    
    # Determine Phi
    phi = theta2(rack_spacing, wt, l_tierod, l_str_arm, 0)
    if phi < phi_lower_bound:
        results = np.full((3, num_fit_points), np.nan)
    
        return results
    
    else:
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
simulation_results = cartesian_product_on_the_fly_mm(num_fit_points, rack_spacing, l_tierod, l_str_arm)

# Initialize a list to store indices of valid simulations
valid_indices = []

# Filter out NaN-containing results and track valid indices
filtered_simulation_results = []
for index, result in enumerate(simulation_results):
    if not np.isnan(result).any():
        filtered_simulation_results.append(result)
        valid_indices.append(index)

# Update simulation_results with filtered results
simulation_results = filtered_simulation_results

# Running the error calculation
rmse_results = []

for result in simulation_results:
    y_actual_np_vector = result[1, :]
    y_predicted_np_vector = result[2, :]
    rmse = RMSE(y_actual_np_vector, y_predicted_np_vector)
    rmse_results.append(rmse)

# Pair each RMSE value with its original index
indexed_rmse_results = list(enumerate(rmse_results))

# Sort based on RMSE values
indexed_rmse_results.sort(key=lambda x: x[1])

# Separate the indices and sorted RMSE values
sorted_indices, sorted_rmse = zip(*indexed_rmse_results)

# Finding the index of the minimum RMSE in the filtered results
min_rmse = sorted_rmse[0]
min_rmse_filtered_index = rmse_results.index(min_rmse)

# Map this index back to the original index in simulation_results
min_rmse_original_index = valid_indices[min_rmse_filtered_index]

# Calculate the index in each dimension using the original index
index_rack_spacing = (min_rmse_original_index // (num_steps ** 2)) % num_steps
index_l_tierod = (min_rmse_original_index // num_steps) % num_steps
index_l_str_arm = min_rmse_original_index % num_steps

# Retrieve the optimal values
optimal_rack_spacing = rack_spacing[index_rack_spacing]
optimal_l_tierod = l_tierod[index_l_tierod]
optimal_l_str_arm = l_str_arm[index_l_str_arm]

print("Minimum RMSE:", min_rmse, "at index", min_rmse_original_index)
print("Optimal Geometry:")
print("Rack Spacing:", optimal_rack_spacing)
print("Tierod Length:", optimal_l_tierod)
print("Steering Arm Length:", optimal_l_str_arm)

# My Stuff
print(f'\nlen sorted:{len(sorted_rmse)}')
print(f'first 5 rmse: {sorted_rmse[0:5]}')


# import matplotlib.pyplot as plt
# import matplotlib.animation as animation

# # Assuming you have the simulation_results and rmse_results from your simulations
# # simulation_results should be a list where each item is a numpy array of the form: [theta_i, theta_o, theta_o_ideal]
# # rmse_results should be a list of corresponding RMSE values

# # Pair each RMSE value with its original index
# indexed_rmse_results = list(enumerate(rmse_results))

# # Sort based on RMSE values
# indexed_rmse_results.sort(key=lambda x: x[1])

# # Extract the indices of the sorted RMSE values
# sorted_indices = [index for index, _ in indexed_rmse_results]

# # Reorder the simulation_results based on the sorted_indices
# sorted_simulation_results = [simulation_results[i] for i in sorted_indices]

# # Initialize the figure for animation
# fig, ax = plt.subplots()

# # Animation function
# def animate(i):
#     ax.clear()
#     result = sorted_simulation_results[i]
#     theta_i, theta_o, theta_o_ideal = result
#     ax.plot(theta_i, theta_o, label='Theta_i vs Theta_o')
#     ax.plot(theta_i, theta_o_ideal, label='Theta_i vs Theta_o_ideal')
#     ax.set_title(f"Frame {i+1} (RMSE: {indexed_rmse_results[i][1]:.2f})")
#     ax.legend()

# # Create animation
# ani = animation.FuncAnimation(fig, animate, frames=min(100, len(sorted_simulation_results)), interval=250)

# # Saving the animation as a GIF
# # Adjust the file path as needed for your system
# ani.save('simulation_animation.gif', writer='pillow', fps=4)
# plt.close()
    
#if __name__ == '__main__':
#    everything()

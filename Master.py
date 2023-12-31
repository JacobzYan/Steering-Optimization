# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 20:03:07 2023

Authors: Tristan Houy, Jacob Yan, Edward Kim

Copyright: Fri Nov 10 20:03:07 2023, Tristan Houy, Jacob Yan, Edward Kim, All rights reserved.
"""

from numba import jit, prange
import numpy as np
import matplotlib.pyplot as plt
'''
-------------------------------------------- INPUT INFO --------------------------------------------
Inputs:

An object with the following public attributes:

num_steps:
    int
    Number of steps variable ranges will be divided into
num_fit_points:
    int
    number of points used to find error on graph
phi_lower_bound:
    float
    lower bound of Phi
wb:
    float
    car wheelbase
x_travel:
    float
    half of rack and pinion stroke
w_track:
    float
    track width
l_rack:
    float
    eye to eye length of steering rack
rack_spacing:
    list of 2 floats
    Rack spacing possible range
l_tierod:
    list of 2 floats
    Tierod length possible range
l_str_arm:
    list of 2 floats
    Steering range possible length
num_graphs:
    int
    number of worse fits to plot in addition to best fit
fig:
    matplotlib figure
    figure to pass fig info to. Make sure to pass a figure number when creating eg. fig = plt.figure(1)


-------------------------------------------- OUTPUT INFO --------------------------------------------
fig: 
    matplotlib figure
    a populated figure with best fits. display with .show()
[optimal_rack_spacing, optimal_l_tierod, optimal_l_str_arm]
    list of 3 floats
    optimal geomery
'''

def Simulate(input_geom):
    num_steps = input_geom.num_steps
    num_fit_points = input_geom.num_fit_points
    phi_lower_bound = input_geom.phi_lower_bound
    wb = input_geom.wb
    x_travel = input_geom.x_travel
    w_track = input_geom.w_track
    l_rack = input_geom.l_rack
    # rack_spacing = input_geom.rack_spacing
    rack_spacing_lower = input_geom.rack_spacing_lower
    rack_spacing_upper = input_geom.rack_spacing_upper
    # l_tierod = input_geom.l_tierod
    l_tierod_lower = input_geom.l_tierod_lower
    l_tierod_upper = input_geom.l_tierod_upper
    # l_str_arm = input_geom.l_str_arm
    l_str_arm_lower = input_geom.l_str_arm_lower
    l_str_arm_upper = input_geom.l_str_arm_upper
    num_graphs = input_geom.num_graphs
    fig = input_geom.f
    '''-------------------------------------------------OPTIMIZATION PARAMETERS---------------------------------------------------------'''
    
    wt = (w_track - l_rack)/2 # Equivalent steering thickness [mm]
 

    # Define initial variable vectors
    rack_spacing=np.linspace(rack_spacing_lower, rack_spacing_upper, num_steps)
    l_tierod=np.linspace(l_tierod_lower, l_tierod_upper, num_steps)
    l_str_arm=np.linspace(l_str_arm_lower, l_str_arm_upper, num_steps)

    # Define helper function to pull parameters
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
            x_i = np.linspace(0, -x_travel, num_fit_points)
            x_o = np.linspace(0, x_travel, num_fit_points)
        
            # Determine corresponding theta 2 lists
            theta2_i = theta2(rack_spacing, wt, l_tierod, l_str_arm, x_i)
            theta2_o = theta2(rack_spacing, wt, l_tierod, l_str_arm, x_o)
            
            # Determine corresponding theta_i and theta_o
            theta_i = np.pi - wheel_angle(theta2_i, phi)
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


    # Helper function to add wheel offset to steering arm angle
    @jit(nopython=True, parallel=True)
    def wheel_angle(theta2, phi):
        return theta2 + np.pi/2 - phi

    # Helper function to calculate ideal outer wheel angle
    @jit(nopython=True, parallel=True)
    def theta_o_ideal_eq(wb, wt, theta_i):
        return np.pi/2 - np.arctan((wb) / (wb/np.tan(np.pi/2 - theta_i) + 2*wt))

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

    # Collect RMSE values
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

    # Output Ideal value information
    print("Minimum RMSE:", min_rmse, "at index", min_rmse_original_index)
    print("Optimal Geometry:")
    print("Rack Spacing:", optimal_rack_spacing)
    print("Tierod Length:", optimal_l_tierod)
    print("Steering Arm Length:", optimal_l_str_arm)

    # Cacluate performance from geometry
    [theta_i_plot, theta_o_plot, theta_o_ideal_plot] = sim(optimal_rack_spacing, wt, optimal_l_tierod, optimal_l_str_arm, wb, x_travel, num_fit_points, phi_lower_bound)

    # Plotting setup
    # plt.figure()
    fig.add_subplot(1,1,1)
    # Save plotting range
    x_range = [min(theta_i_plot)-0.05, max(theta_i_plot)+0.05]
    y_range = [min(theta_o_ideal_plot)-0.05, max(theta_o_ideal_plot)+0.05]
    y_ticks = []
    for i in list(np.linspace(y_range[0], y_range[1], 5)):
        y_ticks.append(round(i, 3))


    # Plot ideal solution and best optimized solution
    plt.plot(theta_i_plot, theta_o_ideal_plot, 'k-', linewidth = 8, label = 'Ideal Curve')
    plt.plot(theta_i_plot, theta_o_plot, 'r--', linewidth = 2, label = f'Best Fit Curve: rsme = {min_rmse}')

    # Calculate and plot curves for the next 100 best fitting curves 

    for i in sorted_rmse[1:num_graphs+1]:

        min_rmse_filtered_index = rmse_results.index(i)

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

        # Cacluate performance from geometry
        [theta_i_plot, theta_o_plot, theta_o_ideal_plot] = sim(optimal_rack_spacing, wt, optimal_l_tierod, optimal_l_str_arm, wb, x_travel, num_fit_points, phi_lower_bound)
        plt.plot(theta_i_plot, theta_o_plot, '--', 'color', 'tab:gray', linewidth = 0.25)

    # Format figure
    
    plt.title(f'Comparison of inner and outer wheel curves with step count of {num_steps}')
    plt.xlabel('Inner Wheel Angle [rad]')
    plt.ylabel('Outer Wheel Angle [rad]')
    plt.xlim(x_range)
    plt.ylim(y_range)
    plt.legend(loc='best')
    plt.yticks(y_ticks, y_ticks) 
    # plt.show()

    return fig, [optimal_rack_spacing, optimal_l_tierod, optimal_l_str_arm]


# -------------------------------------------------------Tester---------------------------------------------------------------------------------------
if __name__ == "__main__":

    class Geom():
         def __init__(self, num_steps, num_fit_points, phi_lower_bound, wb, x_travel, w_track, l_rack, rack_spacing_lower, rack_spacing_upper, l_tierod_lower, l_tierod_upper, l_str_arm_lower, l_str_arm_upper, num_graphs, f):
            self.num_steps = num_steps
            self.num_fit_points = num_fit_points
            self.phi_lower_bound = phi_lower_bound
            self.wb = wb
            self.x_travel = x_travel
            self.w_track = w_track
            self.l_rack = l_rack
            self.rack_spacing_lower = rack_spacing_lower
            self.rack_spacing_upper = rack_spacing_upper
            self.l_tierod_lower = l_tierod_lower
            self.l_tierod_upper = l_tierod_upper
            self.l_str_arm_lower = l_str_arm_lower  
            self.l_str_arm_upper = l_str_arm_upper
            self.num_graphs = num_graphs
            self.f = f

    # Simulation parameters
    num_steps = 10 # Define the number of steps
    num_fit_points = 100 # Define granularity

    # Constants
    phi_lower_bound = np.radians(-15) # Lower bound for phi in radians [Deg] -> [Rad]
    wb = 2000 # Wheelbase [mm]
    x_travel = 80 # Steering rack travel [mm]
    w_track = 800 # Track width [mm]
    l_rack = 300 # Steering rack length [mm]

    # Dependent Variables
    wt = (w_track - l_rack)/2 # Equivalent steering thickness [mm]

    # Variables
    rack_spacing = [50.2, 450] # Front/back distance between steering rack axis and control arm bearing mounting [mm]
    rack_spacing_lower = rack_spacing[0]
    rack_spacing_upper = rack_spacing[1]

    l_tierod = [50, 350] # Tierod length [mm]
    l_tierod_lower = l_tierod[0]
    l_tierod_upper = l_tierod[1]

    l_str_arm = [50.1, 800] # Distance from control arm mounts to steering arm mount [mm]
    l_str_arm_lower = l_str_arm[0]
    l_str_arm_upper = l_str_arm[1]
    
    # Plotting parameters
    num_graphs = 100 # Number of next best fits to plot

    # Call function
    f = plt.figure(1)
    tester = Geom(num_steps, num_fit_points, phi_lower_bound, wb, x_travel, w_track, l_rack, rack_spacing_lower, rack_spacing_upper, l_tierod_lower, l_tierod_upper, l_str_arm_lower, l_str_arm_upper, num_graphs, f)
    
    f, geom = Simulate(tester)

    # Display
    print(f'Geom: {geom}')
    plt.show()
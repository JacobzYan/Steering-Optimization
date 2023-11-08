# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 22:49:12 2023

Author: Tristan Houy

Copyright: Tue Nov  7 22:49:12 2023, Tristan Houy, All rights reserved.
"""

from numba import jit, prange
import numpy as np

@jit(nopython=True, parallel=True)
def generate_cartesian_product():
    a = np.arange(800, 900, 0.1)
    l_1 = np.arange(600, 700, 0.1)
    l_2 = np.arange(400, 500, 0.1)
    
    # Calculate the number of combinations
    num_combinations = a.size * l_1.size * l_2.size

    # Pre-allocate a NumPy array to hold all combinations
    cartesian_product_array = np.empty((num_combinations, 3), dtype=np.float32)
    
    # Fill the array with combinations
    # The use of a flat index is crucial here because we're filling a 2D array
    index = 0
    for i in prange(a.size):
        for j in range(l_1.size):
            for k in range(l_2.size):
                cartesian_product_array[index] = [a[i], l_1[j], l_2[k]]
                index += 1
                
    return cartesian_product_array

# Now `test` will be a NumPy array containing all combinations
test = generate_cartesian_product()
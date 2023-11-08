# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 23:02:49 2023

Author: Tristan Houy

Copyright: Tue Nov  7 23:02:49 2023, Tristan Houy, All rights reserved.
"""

from numba import jit, prange
import numpy as np

@jit(nopython=True, parallel=True)
def generate_cartesian_product():
    start_a = 800.0
    step_a = 0.1
    size_a = int((900 - start_a) / step_a)
    
    start_l_1 = 600.0
    step_l_1 = 0.1
    size_l_1 = int((700 - start_l_1) / step_l_1)
    
    start_l_2 = 400.0
    step_l_2 = 0.1
    size_l_2 = int((500 - start_l_2) / step_l_2)
    
    num_combinations = size_a * size_l_1 * size_l_2

    cartesian_product_array = np.empty((num_combinations, 3), dtype=np.float32)
    
    for i in prange(size_a):
        a_val = start_a + i * step_a
        for j in range(size_l_1):
            l_1_val = start_l_1 + j * step_l_1
            for k in range(size_l_2):
                l_2_val = start_l_2 + k * step_l_2
                idx = i * size_l_1 * size_l_2 + j * size_l_2 + k
                cartesian_product_array[idx] = [a_val, l_1_val, l_2_val]
                
    return cartesian_product_array

test = generate_cartesian_product()
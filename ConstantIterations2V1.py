# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 11:43:10 2023

Author: Tristan Houy

Copyright: Wed Nov  8 11:43:10 2023, Tristan Houy, All rights reserved.
"""

import numpy as np

def cartesian_product_on_the_fly():
    a=np.arange(800, 810, 0.1, dtype=np.float64)
    l_1=np.arange(600, 610, 0.1, dtype=np.float64)
    l_2=np.arange(400, 410, 0.1, dtype=np.float64)
    
    for i in range(a.size):
        for j in range(l_1.size):
            for k in range(l_2.size):
                # Yield the current combination as a tuple
                yield np.array([a[i], l_1[j], l_2[k]], dtype=np.float64)

# Example usage
for combination in cartesian_product_on_the_fly():
    # Process each combination - do something with each one here
    # For example, print it out
    print(combination)
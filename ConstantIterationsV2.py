# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 21:21:18 2023

Author: Tristan Houy

Copyright: Tue Nov  7 21:21:18 2023, Tristan Houy, All rights reserved.
"""

from numba import jit, prange
import numpy as np

@jit(nopython=True,parallel=True)
def generate_cartesian_product():
    a=np.arange(800, 900, 0.1)
    l_1=np.arange(600, 700, 0.1)
    l_2=np.arange(400, 500, 0.1)
    
    cartesian_product_array=np.empty((a.size, l_1.size, l_2.size, 3), dtype=np.float32)
    for i in prange(a.size):
        for j in range(l_1.size):
            for k in range(l_2.size):
                cartesian_product_array[i, j, k, 0]=a[i]
                cartesian_product_array[i, j, k, 1]=l_1[j]
                cartesian_product_array[i, j, k, 2]=l_2[k]
    return cartesian_product_array

test=generate_cartesian_product()
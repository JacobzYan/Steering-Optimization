# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 12:03:58 2023

Author: Tristan Houy

Copyright: Wed Nov  8 12:03:58 2023, Tristan Houy, All rights reserved.
"""

from numba import jit, prange
import numpy as np
#import cProfile
import timeit

@jit(nopython=True,parallel=False)
def process_combination(a_val,l_1_val,l_2_val):
    return np.array([a_val, l_1_val, l_2_val], dtype=np.float64)

@jit(nopython=True,parallel=True)
def cartesian_product_on_the_fly():
    a=np.arange(800, 900.1, 0.1)
    l_1=np.arange(600, 700.1, 0.1)
    l_2=np.arange(400, 500.1, 0.1)
    
    size=a.size*l_1.size*l_2.size
    print(f"This is the total number of iterations: {size}")
    
    for i in prange(a.size):
        for j in prange(l_1.size):
            for k in prange(l_2.size):
                process_combination(a[i],l_1[j],l_2[k])
                
#cProfile.run("cartesian_product_on_the_fly()")
#Using timeit.timeit
elapsed_time = timeit.timeit("cartesian_product_on_the_fly()", 
                             setup="from __main__ import cartesian_product_on_the_fly", 
                             number=1)
print(f"Elapsed time: {elapsed_time} seconds")
# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 12:48:56 2023

Author: Tristan Houy

Copyright: Wed Nov  8 12:48:56 2023, Tristan Houy, All rights reserved.
"""

from numba import jit, prange
import numpy as np
import timeit

@jit(nopython=True,parallel=False)
def process_combination(a_val,l_1_val,l_2_val):
    return np.array([a_val, l_1_val, l_2_val], dtype=np.float64)

@jit(nopython=True,parallel=True)
def cartesian_product_on_the_fly_mm():
    a=np.linspace(800, 900, 101)
    l_1=np.linspace(600, 700, 101)
    l_2=np.linspace(400, 500, 101)
    
    #size=a.size*l_1.size*l_2.size
    #print(f"This is the total number of iterations: {size}")
    
    for i in prange(a.size):
        for j in prange(l_1.size):
            for k in prange(l_2.size):
                process_combination(a[i],l_1[j],l_2[k])

@jit(nopython=True,parallel=True)
def optimized_theta_2_linspace():
    theta_2=np.linspace(-np.pi, np.pi, 1001)
    return theta_2

if __name__ == '__main__':
    elapsed_time_mm = timeit.timeit("cartesian_product_on_the_fly_mm()", 
                                    globals=globals(), 
                                    number=1)
    print(f"Elapsed time for cartesian_product_on_the_fly_mm: {elapsed_time_mm} seconds")

    elapsed_time_rad = timeit.timeit("optimized_theta_2_linspace()", 
                                     globals=globals(), 
                                     number=1)
    print(f"Elapsed time for optimized_theta_2_linspace(): {elapsed_time_rad} seconds")

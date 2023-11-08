# -*- coding: utf-8 -*-
"""
Created on Wed Nov  8 11:52:50 2023

Author: Tristan Houy

Copyright: Wed Nov  8 11:52:50 2023, Tristan Houy, All rights reserved.
"""

from numba import jit, prange
import numpy as np

@jit(nopython=True,parallel=False)
def process_combination(a_val,l_1_val,l_2_val):
    array=np.array([a_val, l_1_val, l_2_val], dtype=np.float64)
    print(array)
    #return np.array([a_val, l_1_val, l_2_val], dtype=np.float64)

@jit(nopython=True,parallel=True)
def cartesian_product_on_the_fly():
    a=np.arange(800, 810, 0.1)
    l_1=np.arange(600, 610, 0.1)
    l_2=np.arange(400, 410, 0.1)
    
    for i in prange(a.size):
        for j in prange(l_1.size):
            for k in prange(l_2.size):
                process_combination(a[i],l_1[j],l_2[k])
                
cartesian_product_on_the_fly()
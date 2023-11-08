# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 21:03:45 2023

Author: Tristan Houy

Copyright: Tue Nov  7 21:03:45 2023, Tristan Houy, All rights reserved.
"""

import numpy as np
import itertools

a=np.arange(0, 1001, 1, dtype=float)
l_1=np.arange(0, 1001, 1, dtype=float)
l_2=np.arange(0, 1001, 1, dtype=float)

#Cartesian product
cartesian_product=list(itertools.product(a,l_1,l_2))
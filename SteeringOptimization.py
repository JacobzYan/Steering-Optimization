# Optimization portion of algorithm
# Set list of parameters
# Outputs Optimized geometry given parameters
from SteeringSimulation import sim
from SteeringGeometry import SteeringGeometry as str




# Notes:
'''
- All variables are public and in mm
    call/set with objName.varName
- See drawn diagrams with the following conversion:

wt -> wt
    (wt is defined by changing w_track and l_rack with the equation wt = (w_track- l_rack)      )
    (wt is not updated when w_track or l_rack change so be sure to update the value of wt after - HAS BEEN IMPLEMENTED IN SteeringSimulation )
l1 -> l_tierod
l2 -> l_str_arm
a -> rack_spacing
wb -> wb


'''



# Sample
a = str()
#...
b = sim(a, 100) # b is error
print(b)

a.l_rack = 50
b = sim(a, 100) # b is error
print(b)

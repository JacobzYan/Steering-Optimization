# Simulation Function
# Takes in geometry object and outputs matched numerical vectors of objects

from SteeringGeometry import SteeringGeometry as str
import numpy as np


# Returns an error value for given geometry
def sim(geom: str, num_fit_points: int):
    
    # # Establish theta 2 range
    # theta2 = np.linspace(-np.pi, np.pi, num_fit_points)
    # geom.wt = geom.w_track - geom.l_rack
    # geom.phi = 
    # x = geom.wt / 2 - geom.l_tierod * np.cos(np.arcsin(1/geom.l_tierod * (geom.rack_spacing - (geom.l_str_arm * np.sin(theta2))))) - geom.l_str_arm * np.cos(theta2)
    # print(x)
    
    
    
    
    










    ## Fake Error value, should cause all values to converge to 50
    # print(f'the works: {geom.vars()}')
    error = 0
    for i in geom.vars():
        try:
            error += (float(geom.vars()[i]) - 50.0)**2
        except:
            pass

    return error



a = str()
print(a)
b = sim(a, 10)
print(f'b: {b}')
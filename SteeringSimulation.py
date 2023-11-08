# Simulation Function
# Takes in geometry object and outputs matched numerical vectors of objects

# from SteeringGeometry import SteeringGeometry as str
from SteeringGeometry import SteeringGeometry as str

# Returns an error value for given geometry
def sim(geom: str):
    
    
    
    
    
    










    ## Fake Error value, should cause all values to converge to 50
    # print(f'the works: {geom.vars()}')
    error = 0
    for i in geom.vars():
        try:
            error += (float(geom.vars()[i]) - 50.0)**2
        except:
            pass

    return error






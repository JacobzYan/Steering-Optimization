#  Class that defines relevant info about steering geometry
import warnings


class SteeringGeomtery:
    

    def __init__(self, **args):
        
        ## Default values DEFINE NEW VARAIBLES IN THIS SECTION
        # Constants
        self.wb = 1500 # Wheelbase [mm]
        self.x_travel = 200 # Steering rack travel [mm]
        self.w_track = 1 # Track width [mm]
        self.l_rack = 0.5 # Steering rack length [mm]
        # Variables
        self.rack_spacing = 500 # Horizontal distance between control arm bearing mounting and steering rack axis
        self.l_tierod = 20 # Tierod length [mm]
        self.l_str_arm = 40 # distance from control arm mounts to steering arm mount [mm]
        self.phi = 5 # Steering Arm offset angle [deg]


        ## Count number of variables
        num_var = len(filter(lambda x: x[0,1] != '--', dir()))
        num_changed = 0;

        # Read in init values
        for i in args.keys():
            # Sanitize to only existing variables
            try:
                exec(i)
                exec(f'self.{i} = {args[i]}')
                num_changed += 1
            except:
                print(f'WARNING: {i} = {args[i]} IS AN INVALID INPUT')
        
        # Warn if default values still exist
        if(num_changed != num_var):
            warnings.warn(f"WARNING NOT ALL VARAIBLES CHANGED FROM DEFAULT VALUES")

        # Define Equivalent Thickness wt
        self.wt = (self.w_track - self.l_rack)/2.0 # Equivalent steering thickness [mm]

    def __str__(self):
        # Create a list of defined variables
        vars = filter(lambda x: x[0,1] != '--', dir())

        # For each variable, print the name and value
        for i in vars:
            temp = -1;
            exec(f'temp = {i}')
            print(f'{i}: {temp}')
        
    def getVar(**var_names):
        # Create a list of defined variables
        vars = filter(lambda x: x[0,1] != '--', dir())
        
        for i in var_names:
            i



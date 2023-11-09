#  Class that defines relevant info about steering geometry
import numpy as np





class SteeringGeometry:
    obj_count = 0


    def __init__(self, **args):
        # Track Object Names
        SteeringGeometry.obj_count += 1
        self.obj_name = f'Geometry {SteeringGeometry.obj_count}'

        ## Default values DEFINE NEW VARAIBLES IN THIS SECTION
        # Constants
        self.wb = 1500 # Wheelbase [mm]
        self.x_travel = 30 # Steering rack travel [mm]
        self.w_track = 800 # Track width [mm]
        self.l_rack = 300 # Steering rack length [mm]
        # Variables
        self.rack_spacing = 200 # Front/back distance between steering rack axis and control arm bearing mounting
        self.l_tierod = 250 # Tierod length [mm]
        self.l_str_arm = 100 # distance from control arm mounts to steering arm mount [mm]
        self.phi = 11*np.pi/180 # Steering Arm offset angle [deg]
        # Dependent Variables
        self.wt = self.w_track - self.l_rack # Equivalent steering thickness [mm]

        ## Count number of variables
        self.var_names = list(filter(lambda x: x[0:2] != '__', dir(self)))
        
        num_var = len(self.var_names)
        num_changed = 0;
        
        # Read in init values
        for i in args.keys():
            # Sanitize to only existing variables
            if i in self.var_names:
                exec(f'self.{i} = {args[i]}')
                num_changed += 1
            else:
                print(f'WARNING: {i} = {args[i]} IS AN INVALID INPUT')
        
        # Warn if default values still exist
        if(num_changed != num_var):
            print("WARNING NOT ALL VARAIBLES CHANGED FROM DEFAULT VALUES")


    # Returns a dictionary of all variables
    def vars(self):
        return self.__dict__


    # Returns a useable list of 
    def __str__(self):
        # For each variable, print the name and value
        temp = ''
        temp += f'{self.obj_name}:\n\t'
        # Add each variable
        temp += f'wb = {self.wb}\n\t'
        temp += f'w_track = {self.w_track}\n\t'
        temp += f'wt = {self.wt}\n\t'
        temp += f'x_travel = {self.x_travel}\n\t'
        temp += f'l_rack = {self.l_rack}\n\t'
        temp += f'rack_spacing = {self.rack_spacing}\n\t'
        temp += f'l_tierod = {self.l_tierod}\n\t'
        temp += f'l_str_arm = {self.l_str_arm}\n\t'
        temp += f'phi = {self.phi}\n'

        # Not sure why this doesn't work :(
        '''      
        temp2 = -1 # defines each variable
        for i in self.var_names:
            temp2 = self.l_rack
            a = f"temp2 = self.{str(i)}"
            exec(a)
            temp += f'{i}: {temp2}\n'
        '''
        return temp

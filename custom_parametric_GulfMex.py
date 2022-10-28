# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 17:04:56 2022

@author: rrolph
"""

import pandas as pd
from itertools import product
from copy import deepcopy
import os

from ORBIT import ProjectManager, load_config
from ORBIT.parametric import LinearModel
from ORBIT.core.library import initialize_library

depths = [10, 20, 30, 40, 50, 60]  # m. water depth
turbines = ["15mw", "17mw", "17mw-lowSP"]
distances = [10, 50, 100, 150, 200, 300, 400, 500, 600] # km. distance from site to port

DIR = os.path.split(__file__)[0]
LIBRARY= os.path.join(DIR, "library")
print(LIBRARY)
initialize_library(LIBRARY)

# Create or load a base config of constant inputs
base_config = {
    
    # Constant Inputs
    "wtiv": "example_wtiv",
    #feeder: "dict | str (optional)",
    #num_feeders: "int (optional)",
    "plant": {"num_turbines": 1},
    #port:
        #num_cranes: #"int (optional, default: 1)",
        #monthly_rate: #"USD/mo (optional)",
        #name: # "str (optional)",
    
    # Constant Modules
    "design_phases": [], # We are providing the design from Mayank's jacket yaml file, not an ORBIT design module.
    "install_phases": [
        "JacketInstallation"
    ]
}

# Create a list to hold results
data = []

# Loop through inputs / input files as necessary
for depth, turbine, dts in product(depths, turbines, distances):

    # Copy base config into new object so that you don't impact the base config with any dict operations
    config = deepcopy(base_config)    

    # Load scenario specific info that changes with loop
    dict_scenario = {
        'site': {'depth': depth, 'distance': dts},        
        }
    
    # combine configs
    config = ProjectManager.merge_dicts(config, dict_scenario)
    sub_config_fp = f"C:/Users/rrolph/OneDrive - NREL/Projects/Gulf_of_Mexico/library"        
    #sub_config = load_config(sub_config_fp)
    jacket_config = load_config(f"{sub_config_fp}/jackets/{turbine}/{turbine}_{depth}m.yaml")
    turbine_config = load_config(f"{sub_config_fp}/turbines/{turbine}/{turbine}.yaml")

    # Merge new base and scenario specific configs
    #config = ProjectManager.merge_dicts(sub_config, base_config)
    config = ProjectManager.merge_dicts(config, jacket_config)
    config = ProjectManager.merge_dicts(config,turbine_config)

    # Run ORBIT, pass weather if necessary
    project = ProjectManager(config, library_path=LIBRARY)
    project.run()

    # Collect required inputs and results
    res = {
        "site_depth": project.config["site.depth"],
        "distance_to_shore": project.config["site.distance"],
        "jacket_install": project.system_costs['JacketInstallation'],
    }

    data.append(res)

# Create DataFrame
df = pd.DataFrame(data)

# Save dataframe
df.to_pickle('outputs/jacket_installation_cost_1_turbine.pkl')

'''
sub = df.loc[df.site_depth == 10]
sub.iloc[10]
Out[62]: 
site_depth           1.000000e+01
distance_to_shore    5.000000e+01
jacket_install       3.353009e+07
Name: 10, dtype: float64

sub.iloc[0]
Out[63]: 
site_depth           1.000000e+01
distance_to_shore    1.000000e+01
jacket_install       3.321548e+07
Name: 0, dtype: float64
'''


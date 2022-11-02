# -*- coding: utf-8 -*-
"""
Created on Thu Oct 27 17:04:56 2022

...... one equation for each turbine rating .......

@author: rrolph
"""

import pandas as pd
from itertools import product
from copy import deepcopy
import os
from scipy.optimize import curve_fit
#from mpl_toolkits.mplot3d import axes3d, Axes3D
import numpy as np
import matplotlib.pyplot as plt


from ORBIT import ProjectManager, load_config
from ORBIT.parametric import LinearModel
from ORBIT.core.library import initialize_library

# define paths
fig_path = 'C:/Users/rrolph/OneDrive - NREL/Projects/Gulf_of_Mexico/plots_from_modelling_ORBIT_output/'

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
    
    
    ## debug distance vs. transit time
    if (depth == 60 and dts == 600 and turbine == '15mw') or (depth == 10 and dts == 600 and turbine == '15mw') or (depth == 10 and dts == 200 and turbine == '15mw'):
        df_actions = pd.DataFrame(project.actions)
        sub_actions = df_actions.loc[df_actions['phase']=='JacketInstallation']
        sub_actions.action
        print('site distance is: ' + str(project.config["site.distance"]) + '. Depth is ' + str(project.config["site.depth"]))
        print(sub_actions[['action','duration', 'cost']])
        ##

    # Collect required inputs and results
    res = {
        "site_depth": project.config["site.depth"],
        "distance_to_shore": project.config["site.distance"],
        "jacket_system_cost": project.system_costs['JacketInstallation'],
        "jacket_install_cost": project.installation_costs['JacketInstallation'],
        "turbine_rating": project.config["turbine.turbine_rating"],
        "turbine_name": turbine
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

## Plot some results

# create 3D plane equation for model fit
def func(data, a, b, c):  # make sure data is a list, with first index dts, and 2nd index site depth
    dts = data[0]
    site_depth = data[1]
    return a*dts + b*site_depth + c    
    
def plot_3d(df, turbine_rating, fig_path):  # df is the dataframe that contains information for all or one turbines
    df = df[df.turbine_rating==turbine_rating]
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(projection = '3d')
    # data
    ax.plot(df.distance_to_shore.values, df.site_depth.values, df.jacket_install_cost.values)
    ax.set_xlabel('Distance to shore [km]')
    ax.set_ylabel('Water depth [m]')
    ax.set_zlabel('Jacket install cost [USD]')
    plt.savefig(fig_path + 'ORBIT_output_dts_depth_installCost_' + str(turbine_rating) + '.png') # bbox_inches='tight')

    # find model parameters. jacket_install_cost = f(dts, depth)
    params, pcov = curve_fit(func, [df.distance_to_shore.values, df.site_depth.values], df.jacket_install_cost)

    # create surface model
    # set up data points for calculating surface model
    model_dts_data = np.linspace(min(df.distance_to_shore.values), max(df.distance_to_shore.values),len(df))
    model_depth_data = np.linspace(min(df.site_depth.values), max(df.site_depth.values), len(df))

    # create coordinate arrays
    DTS, DEPTH = np.meshgrid(model_dts_data, model_depth_data)
    # calculate Z coordinate array
    INSTALL_COST = func([DTS, DEPTH], *params)

    # plot new 3D plot with data and model overlaid
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(projection = '3d')
    # "data" (output by ORBIT)
    ax.plot(df.distance_to_shore.values, df.site_depth.values, df.jacket_install_cost.values)
    # model data
    ax.plot_surface(DTS, DEPTH, INSTALL_COST)
    ax.set_xlabel('Distance to shore [km]')
    ax.set_ylabel('Water depth [m]')
    ax.set_zlabel('Jacket install cost [USD]')
    plt.savefig(fig_path + 'model_and_data_dts_depth_installCost_' + turbine + '.png') # bbox_inches='tight')
    
    return params, pcov

# Call each turbine rating
for turbine in turbines:
    if turbine == '15mw':
        turbine_rating = 15.0
    if turbine == '17mw' or '17mw-lowSP':
        turbine_rating = 17.0
    params, pcov = plot_3d(df, turbine_rating, fig_path)
    print('Plot generated and saved for turbine: ' + turbine)
    print('Model equation for ' + turbine + ': ' + 'jacket_install_cost = ' + str(params[0]) + '*dts + ' + str(params[1]) + '*site_depth + ' + str(params[2]))

'''
    Output of above code:
    Plot generated and saved for turbine: 15mw
    Model equation for 15mw: jacket_install_cost = 1023.9726027397224*dts + 136.52968036531928*site_depth + 2502420.091324202
    Plot generated and saved for turbine: 17mw
    Model equation for 17mw: jacket_install_cost = 1023.9726027397224*dts + 136.52968036531928*site_depth + 2502420.091324202
    Plot generated and saved for turbine: 17mw-lowSP
    Model equation for 17mw-lowSP: jacket_install_cost = 1023.9726027397224*dts + 136.52968036531928*site_depth + 2502420.091324202
'''
# Test model with data at a random point
# 15mw 
dts = 150 # km
site_depth = 50
turbine = '15mw'
if turbine == '15mw':
    jacket_install_cost_modelled = 1023.9726027397224*dts + 136.52968036531928*site_depth + 2502420.091324202
print('jacket_install_cost_modelled for dts ' + str(dts) + ' and depth ' + str(site_depth) + ': ' + str(jacket_install_cost_modelled))
#jacket_install_cost_ORBIT = 
# Note the below will only work if dts and site_depth exist in ORBIT inputs
if turbine == '15mw':
    jacket_install_cost_orbit = df.loc[(df['distance_to_shore']==dts) & (df['site_depth']==site_depth) & (df['turbine_name']==turbine)].jacket_install_cost
    print('jacket install cost from ORBIT: ' + str(jacket_install_cost_orbit.values))



'''
## Plot 2D selected slices

# plot just one depth 
df_15mw_30m = df_15mw[df_15mw.site_depth==30]
fig, ax = plt.subplots(1,1)
ax.plot(df_15mw_30m.distance_to_shore, df_15mw_30m.jacket_install_cost)
ax.set_xlabel('Distance to shore [km]')
ax.set_ylabel('Jacket install cost [USD]')
fig = plt.gcf()
fig.set_size_inches(8, 6)
plt.savefig('dts_vs_jacket_install_30m_depth.png', bbox_inches='tight')

# plot just one distance to shore 
df_15mw_200km = df_15mw[df_15mw.distance_to_shore==200]
fig, ax = plt.subplots(1,1)
ax.plot(df_15mw_200km.site_depth, df_15mw_200km.jacket_install_cost)
ax.set_xlabel('Site depth [m]')
ax.set_ylabel('Jacket install cost [USD]')
fig = plt.gcf()
fig.set_size_inches(8, 6)
plt.savefig('depth_vs_jacket_install_200m_dts.png', bbox_inches='tight')

# last loop 
df_actions = pd.DataFrame(project.actions)
sub_actions = df_actions.loc[df_actions['phase']=='JacketInstallation']
# See that transit is only 1x, because 1 turbine....
sub_actions.action # look for 'Transit'
sub_actions[0:5][['action','duration', 'cost']]
#Out[193]: 
#                    action  duration
#0                 Mobilize     168.0
#1            Fasten Jacket      12.0
#2  Fasten Transition Piece       8.0
#3                  Transit      60.0
#4          Position Onsite       2.0

sub_actions[['action','duration', 'cost']]
'''






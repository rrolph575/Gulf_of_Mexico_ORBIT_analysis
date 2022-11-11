"""Primary analysis script."""


import numpy as np
import pandas as pd
import datetime as dt
from copy import deepcopy
import os

from ORBIT import ProjectManager, load_config
from ORBIT.core.library import initialize_library

# Import soft cost analysis module
from construction_finance_param import con_fin_params

DIR = os.path.split(__file__)[0]
LIBRARY= os.path.join(DIR, "library")
print(LIBRARY)
initialize_library(LIBRARY)

WEATHER = pd.read_csv('library/weather/example_weather.csv')

loop_through_configs = False # if True, will run ORBIT for all config files saved in configs/.  If false, specify config file you wish to run:
if loop_through_configs == False:
    specific_config_filename_to_run = 'configs/feeder_jacket_install.yaml'

def run():

    bos_capex = {}
    total_capex = {}
    breakdowns = {}
    installation_times = {}
    bos_capex_per_kW = {}

    if loop_through_configs == True:
        print('this script is for only one config, if more then copy the code for the single config analysis')
    else:
            config = load_config(specific_config_filename_to_run)
            name, extension = os.path.splitext(specific_config_filename_to_run)
            project = ProjectManager(config, library_path=LIBRARY, weather=WEATHER)
            project.run()

            # Collect Results
            bos_capex[name] = project.bos_capex 
            total_capex[name] = project.total_capex

            # Implement update how soft costs are calculated.
            dct = project.capex_breakdown
            dct = {k:[v] for k,v in dct.items()}
            df_bos_breakdown = pd.DataFrame.from_dict(dct, orient="columns")
            soft_dct = con_fin_params(bos=project.bos_capex,
                           turbine_capex=project.turbine_capex,
                           orbit_install_capex=project.installation_capex,
                           plant_cap=project.capacity*1000, per_kW=False)
            print(project.turbine_capex)
            for k,v in soft_dct.items():
                if k != "soft_capex":
                    df_bos_breakdown[k] = v
                else:
                    df_bos_breakdown["Soft"] = v
            df_bos_breakdown = df_bos_breakdown.T
            print(df_bos_breakdown)
            breakdowns = df_bos_breakdown.drop("Soft")  ## Drop soft costs so they are not calculated twice in the sum below. Because the soft cost components are also part of this dataframe.
            #breakdowns[name] = dct
            #"""
            installation_times[name] = project.project_time
            bos_capex_per_kW[name] = project.bos_capex_per_kw

    # Aggregate Results
    bos_capex = pd.Series(bos_capex)
    total_capex = df_bos_breakdown.sum()
    

    times = pd.Series(installation_times)
    bos_capex_per_kW = pd.Series(bos_capex_per_kW)

    # Save Results
    totals = pd.concat([
        bos_capex.rename("BOS"),
        total_capex.rename("Total")
    ], axis=1)
    totals.index = totals.index.rename("")
    totals.iloc[0][1] = totals.iloc[1][1]
    totals = totals.drop(labels=0)
    print(totals)
    totals.to_csv("outputs/scenario_capex.csv")
    bos_capex_per_kW.to_csv("outputs/bos_capex_perkW.csv")
    breakdowns.to_csv("outputs/breakdown.csv")
    times.to_csv("outputs/installation_times.csv")
    
    return project, total_capex, breakdowns, df_bos_breakdown, totals, soft_dct
    

def test_capex_breakdown(name, project):

    expected_capex_categories = [
        "Array System",
        "Export System",
        "Substructure",
        "Offshore Substation",
        "Array System Installation",
        "Export System Installation",
        "Substructure Installation",
        "Offshore Substation Installation",
        "Turbine",
        "Soft",
        "Project"
    ]

    missing = [c for c in expected_capex_categories if c not in project.capex_breakdown.keys()]
    if missing:
        print(f"Missing results for {missing} in {name}.")
        
if __name__ == "__main__":
    #project = run()
    project, total_capex, breakdowns, df_bos_breakdown, totals, soft_dict = run()
   
    #run_parametric()
    
## Categorize project actions
df = pd.DataFrame(project.actions) # This is the entire action list for all phases
action_phases = df['phase'] # These are installation phases
print('Phases are: ' + action_phases.unique()) # These are installation phases

"""
df.keys()
Out[18]: 
Index(['cost_multiplier', 'agent', 'action', 'duration', 'cost', 'level',
       'time', 'phase', 'phase_name', 'max_waveheight', 'max_windspeed',
       'transit_speed', 'location', 'site_depth', 'num_vessels'],
      dtype='object')
"""
     
#print('anchor mass is: ' + str(project.detailed_outputs['anchor_mass']))
    
    






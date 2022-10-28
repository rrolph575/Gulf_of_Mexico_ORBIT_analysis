# -*- coding: utf-8 -*-
"""
Created on Mon Sep 26 14:41:57 2022


"""

import os
from ParametricORBIT import ModelSet, ROOT, OrbitStandard


#DIR = os.path.split(os.path.abspath(__file__))[0]
DIR = os.getcwd()


if __name__ == "__main__":

    plot_dir = os.path.join(DIR, "plots")

    modelset = ModelSet(
        "configs/",
        "parametric_outputs/outputs.yaml",
        aggregation_set=OrbitStandard,
        ## i think i have to change library to the local one with mayank's configs.
        library=os.path.join(ROOT, "library"), # should be changed to local library but has to interact with loop ? . currently .join(ROOT, 'library') is 'C:\\Users\\rrolph\\OneDrive - NREL\\ParametricOrbit\\ParametricORBIT\\ParametricORBIT\\library'
        overwrite=False,
        plot_dir=plot_dir
    )

    modelset.generate_models()
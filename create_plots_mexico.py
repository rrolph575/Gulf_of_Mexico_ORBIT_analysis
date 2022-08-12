"""Plotting script."""

__author__ = "Matt Shields"
__copyright__ = "Copyright 2022, National Renewable Energy Laboratory"
__maintainer__ = "Matt Shields"
__email__ = "matt.shields@nrel.gov"


import os

import pandas as pd
import matplotlib.pyplot as plt


FIGDIR = os.path.join(os.getcwd(), "figures")
PROJECT_kW = 15000*54


TOTALS = pd.read_csv("outputs/scenario_capex.csv").rename(columns={
    "Unnamed: 0": "scenario",
    "0": "Total CapEx"
})

TOTALS = TOTALS.set_index("scenario")
TOTALS = TOTALS.rename(index={'configs/semisub_OCG': 'OCG-Wind'})
print(TOTALS)


BREAKDOWNS = pd.read_csv("outputs/breakdown.csv").rename(columns={
    "Unnamed: 0": "Category",
})
BREAKDOWNS = BREAKDOWNS.set_index("Category")
BREAKDOWNS = BREAKDOWNS.rename(columns={'configs/semisub_OCG': 'OCG-Wind'})

# Installation times
INSTALL = pd.read_csv("outputs/installation_times.csv").rename(columns={
    "Unnamed: 0": "year",
})
INSTALL = INSTALL.set_index("year")
INSTALL = INSTALL.rename(columns={'configs/semisub_OCG': 'OCG-Wind'})



def total_capex_plots(df):
    """"""

    # Raw CapEx
    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.add_subplot(111)

    df.plot(kind='bar', ax=ax)

    ax.set_xlabel("")
    ax.set_ylabel("CapEx ($)")
    plt.xticks([1], ['']) # remove xtick

    fig.savefig(os.path.join(FIGDIR, "total_capex.png"), bbox_inches='tight')

    # CapEx per kW
    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.add_subplot(111)

    df.divide(PROJECT_kW).plot(kind='bar', ax=ax)

    ax.set_xlabel("")
    ax.set_ylabel("CapEx ($/kW)")
    plt.xticks([1], ['']) # remove xtick
    
    fig.savefig(os.path.join(FIGDIR, "total_per_kW.png"), bbox_inches='tight')

    # LCOE 
    opex = 118
    fcr = .0582
    ncf = .459 

    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.add_subplot(111)

    print('This is the CapEx per kW' + str(df['Total'].divide(PROJECT_kW)))
    print(PROJECT_kW)
    df_lcoe = 1000*(fcr * df['Total'].divide(PROJECT_kW) + opex) / (ncf * 8760)

    print(df_lcoe)
    df_lcoe.plot(kind='bar', ax=ax, rot=45)
    ax.set_xlabel("")
    ax.set_ylabel("LCOE ($/MWh)")
    
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1]) #, loc='upper left')    
    plt.xticks([1], ['']) # remove xtick
    
    fig.savefig(os.path.join(FIGDIR, "LCOE.png"), bbox_inches='tight')

def capex_breakdown_plots(df):
    """"""

    # Raw CapEx
    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.add_subplot(111)

    df[:-7].T.plot(kind='bar', stacked=True, ax=ax).legend(bbox_to_anchor=(1.05, 1))

    ax.set_xlabel("")
    ax.set_ylabel("CapEx ($)")
    
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], bbox_to_anchor=(1.05,1))
    plt.xticks([1], ['']) # remove xtick
    
    fig.savefig(os.path.join(FIGDIR, "capex_breakdown.png"), bbox_inches='tight')

    # Raw CapEx
    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.add_subplot(111)

    df[:-7].divide(PROJECT_kW).T.plot(kind='bar', stacked=True, ax=ax)

    ax.set_xlabel("")
    ax.set_ylabel("CapEx ($/kW)")
    
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1], bbox_to_anchor=(1.05,1))
    plt.xticks([1], ['']) # remove xtick

    fig.savefig(os.path.join(FIGDIR, "breakdown_per_kW.png"), bbox_inches='tight')


def installation_time_plots(df):
    """"""
    fig = plt.figure(figsize=(6, 4), dpi=200)
    ax = fig.add_subplot(111)

    df.divide(24*30).boxplot()

    ax.set_xlabel("")
    ax.set_ylabel("Installation time, months")

    fig.savefig(os.path.join(FIGDIR, "installation_times.png"), bbox_inches='tight')
    

if __name__ == "__main__":

    total_capex_plots(TOTALS)
    capex_breakdown_plots(BREAKDOWNS)
    installation_time_plots(INSTALL)

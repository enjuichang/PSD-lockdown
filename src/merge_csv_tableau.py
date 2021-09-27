import numpy as np
import pandas as pd
import os
import sys
import re

# Paths and Inputs
MainPath = "./" 
FileDir = "./CSV/"
# StaName = sys.argv[1]
StaName = 'stalst_work'
OutFigPath = './PNG'
EvtDir = "./EVTLST"
EvtName = 'evtlst_2021'
avg = "avg_7"
start_basedate = '20210101'

StaNameLIST = open("STALST/"+StaName).read().split("\n")


# Generate Dataframe
for i,sta in enumerate(StaNameLIST):
    FilePath = os.path.join(FileDir,sta+"_avg_"+start_basedate+"base.csv")
    df = pd.read_csv(FilePath).drop(columns='Unnamed: 0')
    if i == 0: plotDF = pd.concat([pd.to_datetime(df['time']),df[avg]], axis=1, keys=['time',sta])
    else: plotDF = plotDF.join(pd.concat([pd.to_datetime(df['time']),df[avg]], axis=1, keys=['time',sta]).set_index('time'), on = 'time')


plotDF.to_csv('tableau_by_loc.csv')
outputDF = pd.melt(plotDF,id_vars=['time'])
outputDF.columns = ['time','location','avg_7']
outputDF.to_csv('tableau_raw.csv')

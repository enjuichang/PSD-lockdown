#!/usr/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import matplotlib
import numpy as np
import datetime as dt
import sys
import os
import re 

# Paths and Inputs
MainPath = "./" 
FileDir = "./CSV/"
StaName = sys.argv[1]
# StaName = "TAP"
OutCSVPath = './CSV'
EvtDir = "./EVTLST"
EvtName = 'evtlst_191201_210815'
start_basedate = '20200101'
end_basedate = '20200131'
avg = "avg_1"
daylight = True

# Station Path
StaPath = os.path.join(MainPath,StaName)
staLIST = open("STALST/stalst_tap").read().split("\n")
staLIST = ["HSN", "BAC"]

# Event list import
EvtPath = os.path.join(EvtDir,EvtName)
evtLIST = open("EVTLST/evtlst_191201_210815").read().split("\n")
# Figure setting

# RE to find station name
FilePath = os.path.join(FileDir,StaName+"_spect_full.csv")
Station = StaName

# Generate Dataframe
plotDF = pd.read_csv(FilePath).drop(columns='Unnamed: 0')
plotDF['time'] = pd.to_datetime(plotDF.time)
col_names = plotDF.columns[1:]

# Only day time
if daylight: plotDF = plotDF.set_index('time').between_time("9:00","17:00").reset_index()

# Select baseline median
base_medianLIST = []

for col in col_names:
    base_median = plotDF.set_index('time').loc[start_basedate:end_basedate][col].median()

    plotDF[col]=(plotDF[col]-base_median)/abs(base_median)*100

    # Compute rolling average
    if avg == "avg_1":
        plotDF[col+"avg_1"] = plotDF.rolling(window = '1D', on = 'time', min_periods = 1)[col].median()
    else:
        plotDF[col+"avg_7"] = plotDF.rolling(window = '7D', on = 'time')[col].median()
    base_medianLIST.append(base_median)

# Input all event start and end dates
evt_start = dt.datetime.strptime(evtLIST[0],"%Y%m%d")
evt_end =  dt.datetime.strptime(evtLIST[-1],"%Y%m%d")

# Generate time list storage
time_count = evt_start
step = dt.timedelta(days = 1)
time_ls = np.array([])

while time_count < (evt_end+dt.timedelta(days=1)):
    time_ls = np.append(time_ls, time_count)
    time_count += step


### Rolling average
# Create output_df
output_df = pd.DataFrame({'time': time_ls})

# Find average base on date
for col in col_names:
    temp = plotDF.groupby([plotDF['time'].dt.date])[col+avg].mean().reset_index()
    # temp = plotDF.groupby([plotDF['time'].dt.date])[col+'avg_7'].mean().reset_index()
    output_df = output_df.set_index('time').join(temp.set_index('time')).reset_index()

# print tails to check
print("Last 20 values: ",plotDF.tail(10))

# Save csv
if avg == "avg_1": avg_output = "avg"
else: avg_output = avg
if daylight:
    CSV_full_file = 'CSV/'+Station + '_'+avg_output+'_daylight_'+start_basedate+'base.csv'
else:
    CSV_full_file = 'CSV/'+Station + '_'+avg+'_output_full_'+start_basedate+'base.csv'

#CSV_full_path = os.path.join(OutCSVPath,CSV_full_file)
output_df.to_csv(CSV_full_file)
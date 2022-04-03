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
from mpl_toolkits.axes_grid1 import make_axes_locatable


# Paths and Inputs
MainPath = "./" 
FileDir = "./CSV/"
# StaName = sys.argv[1]
StaName = 'stalst_n_edit'
OutFigPath = './PNG'
EvtDir = "./EVTLST"
EvtName = 'evtlst_2021'
avg = "avg_7"
start_basedate = '20210101'

# Station Path
# StaPath = os.path.join(MainPath,StaName)
staLIST = open("STALST/stalst_n_edit").read().split("\n")
# staLIST = ["HSN", "BAC"]

# Event list import
EvtPath = os.path.join(EvtDir,EvtName)
evtLIST = open("EVTLST/evtlst_2021").read().split("\n")

# Figure setting
#fig, ax= plt.subplots(figsize=(30,10))
fig, ax= plt.subplots(figsize=(20,10))

# Generate Dataframe
for i,sta in enumerate(staLIST):
    FilePath = os.path.join(FileDir,sta+"_avg_"+start_basedate+"base.csv")
    df = pd.read_csv(FilePath).drop(columns='Unnamed: 0')
    if i == 0: plotDF = pd.concat([pd.to_datetime(df['time']),df[avg]], axis=1, keys=['time',sta])
    else: plotDF = plotDF.join(pd.concat([pd.to_datetime(df['time']),df[avg]], axis=1, keys=['time',sta]).set_index('time'), on = 'time')
    #print(plotDF)

# Mask date

start_date = dt.datetime.strptime(evtLIST[0],"%Y%m%d")
end_date = dt.datetime.strptime(evtLIST[-1],"%Y%m%d")
plotDF['time'] = pd.to_datetime(plotDF['time'])

mask = (plotDF['time'] > start_date) & (plotDF['time'] <= end_date)
plotDF = plotDF.loc[mask].set_index("time")

# Plot configuration
ax = sns.heatmap(plotDF.T,vmin=-2, vmax=2,cmap="viridis", cbar= True,cbar_kws = {"orientation":"horizontal"})
matplotlib.rcParams['ytick.labelsize'] = 30
matplotlib.rcParams['xtick.labelsize'] = 20


# Major ticks every month.
fmt_month = mdates.MonthLocator(interval=1)
ax.xaxis.set_major_locator(fmt_month)

# Minor ticks 15 days.
#fmt_half_month = mdates.DayLocator(interval = 30)
# fmt_half_month = mdates.MonthLocator(interval = 3)
#ax.xaxis.set_minor_locator(fmt_half_month)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
plt.xticks(rotation=0)
#ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))

#plt.show()

# Save figure
OutFigName = 'PNG/'+StaName+"_heatmap_during_"+EvtName+'.png'
# SavePath = os.path.join(OutFigPath,OutFigName)
fig.savefig(OutFigName)
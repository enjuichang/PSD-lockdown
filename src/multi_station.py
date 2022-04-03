#!/usr/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
import numpy as np
import datetime as dt
import sys
import os


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
fig, ax = plt.subplots(figsize=(15,10))

# Generate Dataframe
for i,sta in enumerate(staLIST):
    FilePath = os.path.join(FileDir,sta+"_avg_"+start_basedate+"base.csv")
    df = pd.read_csv(FilePath).drop(columns='Unnamed: 0')
    if i == 0: plotDF = pd.concat([pd.to_datetime(df['time']),df[avg]], axis=1, keys=['time',sta])
    else: plotDF = plotDF.join(pd.concat([pd.to_datetime(df['time']),df[avg]], axis=1, keys=['time',sta]).set_index('time'), on = 'time')

# Mask selected date
start_date = dt.datetime.strptime(evtLIST[0],"%Y%m%d")
end_date = dt.datetime.strptime(evtLIST[-1],"%Y%m%d")
plotDF['time'] = pd.to_datetime(plotDF['time'])

mask = (plotDF['time'] > start_date) & (plotDF['time'] <= end_date)
plotDF = plotDF.loc[mask]

### Plot each station in selected station list
blues = matplotlib.cm.get_cmap("Blues")
len_colors = 0.75/len(staLIST)
for i, sta in enumerate(staLIST):
    plt.plot(plotDF["time"],plotDF[sta], label = sta, color = blues(1-len_colors*i),)

plt.plot(plotDF['time'],plotDF.drop('time', axis =1).mean(axis=1), lw = 2 ,label = "Mean", color = "red")
plt.plot(plotDF['time'],plotDF.drop('time', axis =1).median(axis=1), lw = 2, label = "Median", linestyle = 'dashed',color = "red")

mean_all = plotDF.drop('time', axis =1).mean(axis=1)
std_all = plotDF.drop('time', axis =1).std(axis=1)

under_line = (mean_all-std_all*2)
over_line = (mean_all+std_all*2)
plt.fill_between(plotDF['time'], under_line, over_line, color='r', alpha=.1) 

# Major ticks every 30 days.
fmt_month = mdates.MonthLocator(interval=3)
ax.xaxis.set_major_locator(fmt_month)

# Minor ticks 15 days.
fmt_half_month = mdates.DayLocator(interval = 30)
# fmt_half_month = mdates.MonthLocator(interval = 3)
ax.xaxis.set_minor_locator(fmt_half_month)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m-%d'))
plt.xlabel("Date",fontsize=20)
plt.ylabel("Change (%)",fontsize=20)

# Draw line at lockdown
plt.axvline(dt.datetime(2021,5,15), color = "red", label = "Taipei lockdown")
plt.axvline(dt.datetime(2021,5,19), color = "blue", label = "Taiwan lockdown")

plt.title(f"{StaName} PSD {avg} during {EvtName}",fontsize=25)
plt.legend(bbox_to_anchor=(1.001, 1), loc='upper left')
plt.show()

### Save figure
OutFigName = 'PNG/'+StaName+'_PSD_avg_'+start_basedate+'base_'+EvtName+'.png'
# SavePath = os.path.join(OutFigPath,OutFigName)
fig.savefig(OutFigName)

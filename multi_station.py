#!/usr/bin/python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import datetime as dt
import sys
import os
import seaborn as sns


# Paths and Inputs
MainPath = "./" 
FileDir = "./CSV/"
StaName = sys.argv[1]
OutFigPath = './PNG'
avg = "avg_7"

# Station Path
StaPath = os.path.join(MainPath,StaName)
staLIST = open(StaPath).read().split("\n")[:-1]
# staLIST = ["HSN", "BAC"]

# Figure setting
fig, ax = plt.subplots(figsize=(30,7))

# Generate Dataframe
for i,sta in enumerate(staLIST):
    FilePath = os.path.join(FileDir,sta+"_avg.csv")
    df = pd.read_csv(FilePath).drop(columns='Unnamed: 0')
    if i == 0: plotDF = pd.concat([pd.to_datetime(df['time']),df[avg]], axis=1, keys=['time',sta])
    else: plotDF = plotDF.join(pd.concat([pd.to_datetime(df['time']),df[avg]], axis=1, keys=['time',sta]).set_index('time'), on = 'time')

# Plot Station
for sta in staLIST:
    plt.plot(plotDF["time"],plotDF[sta], label = sta)

# Major ticks every 30 days.
fmt_month = mdates.DayLocator(interval=30)
ax.xaxis.set_major_locator(fmt_month)

# Minor ticks 15 days.
fmt_half_month = mdates.DayLocator(interval = 15)
ax.xaxis.set_minor_locator(fmt_half_month)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
plt.xlabel("Date",fontsize=20)
plt.ylabel("Amplitude [$m^2/s^4/Hz$] [dB]",fontsize=20)

# Draw line at lockdown
plt.axvline(dt.datetime(2021,5,15), color = "red", label = "Taipei lockdown")
plt.axvline(dt.datetime(2021,5,19), color = "blue", label = "Taiwan lockdown")

plt.title(f"Multistation PSD {avg}",fontsize=25)
plt.legend()
# plt.show()

# Save figure
OutFigName = 'Multistation_PSD_avg.png'
SavePath = os.path.join(OutFigPath,OutFigName)
fig.savefig(SavePath)
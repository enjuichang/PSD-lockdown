#!/usr/bin/python
import pandas as pd
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re

# Paths
MainPath = "./" 
FileDir = "./CSV/"
# FileName = sys.argv[1]
OutFigPath = './PNG'

sta_compiler= re.compile(r'[A-Z]')
Station = sta_compiler.findall(FileName)
FilePath = os.path.join(FileDir,FileName)

# Import
df = pd.read_csv("CSV/BAC_avg.csv").drop(columns='Unnamed: 0')
# df = pd.read_csv(FilePath).drop(columns='Unnamed: 0')

# Descreptive Stats
mean = np.nanmean(df['6.2-12.5 Hz'])
std = np.nanstd(df['6.2-12.5 Hz'])

#fig, (ax0, ax1) = plt.subplots(2,1,figsize=(20,20))
fig, ax = plt.subplots(figsize=(30,7))

# Major ticks every 15 days.
fmt_half_month = mdates.DayLocator(interval=15)
ax.xaxis.set_major_locator(fmt_half_month)

# Minor ticks three days.
fmt_three_days = mdates.DayLocator(interval = 3)
ax.xaxis.set_minor_locator(fmt_three_days)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
ax.set_ylim([mean-2.5*std, mean+2.5*std])

df["7_avg"] = df.rolling(window = "7D", on = 'time').mean()
df["3_avg"] = df.rolling(window = "3D", on = 'time').mean()
df["1_avg"] = df.rolling(window = "1D", on = 'time').mean()

plt.xlabel("Date",fontsize=18)
plt.ylabel("Amplitude [$m^2/s^4/Hz$] [dB]",fontsize=18)


plt.plot(df['time'],df["1_avg"], label = "daily avg")
plt.plot(df['time'],df["7_avg"], label = "7-day avg")
plt.plot(df['time'],df["7_avg"], label = "3-day avg")
plt.legend()

# OutFigName = Station+'_PSD_avg.png'
# SavePath = os.path.join(OutFigPath,OutFigName)
# fig.savefig(SavePath)

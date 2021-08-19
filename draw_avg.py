#!/usr/bin/python
import pandas as pd
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
import datetime as dt

# Paths
MainPath = "./" 
FileDir = "./CSV/"
# FileName = sys.argv[1]
FileName = "BAC_full.csv"
OutFigPath = './PNG'
OutCSVPath = './CSV'



sta_compiler= re.compile(r'[A-Z]')
Station = sta_compiler.findall(FileName)
Station = "".join(Station)
FilePath = os.path.join(FileDir,FileName)

# Import
df = pd.read_csv("CSV/"+FileName).drop(columns='Unnamed: 0')
# df = pd.read_csv(FilePath).drop(columns='Unnamed: 0')

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


df['time'] = pd.to_datetime(df['time'])
df["avg_7"] = df.rolling(window = '7D', on = 'time')['6.2 Hz - 12.5 Hz'].mean()
df["avg_3"] = df.rolling(window = '3D', on = 'time')['6.2 Hz - 12.5 Hz'].mean()
df["avg_1"] = df.rolling(window = '1D', on = 'time')['6.2 Hz - 12.5 Hz'].mean()
#print(df)
df.at[[0,1,2,3,4,5,6],"avg_7"] = np.nan
df.at[[0,1,2],"avg_7"] = np.nan

# Descreptive Stats
mean = np.nanmean(df["avg_1"])
std = np.nanstd(df["avg_1"])

# df.loc[(df['avg_7'] < mean-2*std) | (df['avg_7']>mean+2*std), "avg_7"] = np.nan
# df.loc[(df['avg_3'] < mean-2*std) | (df['avg_3']>mean+2*std), "avg_3"] = np.nan
# df.loc[(df['avg_1'] < mean-2*std) | (df['avg_1']>mean+2*std), "avg_1"] = np.nan

print(df['time'].dtype)


ax.set_ylim([mean-3*std, mean+3*std])

plt.xlabel("Date",fontsize=18)
plt.ylabel("Amplitude [$m^2/s^4/Hz$] [dB]",fontsize=18)

# Draw line at lockdown
ax.axvline(dt.datetime.strptime("20210515","%Y%m%d"), color = "red", label = "Taipei lockdown")
ax.axvline(dt.datetime.strptime("20210519","%Y%m%d"), color = "blue", label = "Taiwan lockdown")

plt.plot(df['time'],df["avg_1"], label = "daily avg")
plt.plot(df['time'],df["avg_3"], label = "3-day avg")
plt.plot(df['time'],df["avg_7"], label = "7-day avg")
plt.title(f"{Station} PSD Average")
plt.legend()
plt.show()

# OutFigName = Station+'_PSD_avg.png'
# SavePath = os.path.join(OutFigPath,OutFigName)
# fig.savefig(SavePath)

CSV_full_file = Station + "_avg.csv"
CSV_full_path = os.path.join(OutCSVPath,CSV_full_file)
df.to_csv(CSV_full_path)

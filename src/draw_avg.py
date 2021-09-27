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
FileName = "TCU_full.csv"
OutFigPath = './PNG'
OutCSVPath = './CSV'

# Change Base
start_basedate = '20210101'
end_basedate = '20210201'

# RE to find station name
sta_compiler= re.compile(r'([A-Z]+(\d+)?)')
Station = sta_compiler.findall(FileName)[0][0]
FilePath = os.path.join(FileDir,FileName)

# Import data
df = pd.read_csv(FilePath).drop(columns = 'Unnamed: 0')
print('NA: ',sum(df['6.2 Hz - 12.5 Hz'].isna()))
print('Length: ',len(df['6.2 Hz - 12.5 Hz']))
print(df)
df['time'] = pd.to_datetime(df.time)

# Select baseline median
if sum(df.set_index('time').loc[start_basedate:end_basedate]['6.2 Hz - 12.5 Hz'].isna()) != len(df.set_index('time').loc[start_basedate:end_basedate]['6.2 Hz - 12.5 Hz']):
    base_median = df.set_index('time').loc[start_basedate:end_basedate]['6.2 Hz - 12.5 Hz'].median()
elif sum(df.set_index('time').loc['20210101':'20210201']['6.2 Hz - 12.5 Hz'].isna()) != len(df.set_index('time').loc['20210101':'20210201']['6.2 Hz - 12.5 Hz']):
    base_median = df.set_index('time').loc['20210101':'20210201']['6.2 Hz - 12.5 Hz'].median()
else:
    base_median = df['6.2 Hz - 12.5 Hz'].median()
print(base_median)

### Set up figure
fig, ax = plt.subplots(figsize=(30,7))
# Major ticks every 6 months
fmt_six_months = mdates.MonthLocator(interval = 6)
ax.xaxis.set_major_locator(fmt_six_months)
# Minor ticks three months.
fmt_three_months = mdates.MonthLocator(interval = 3)
ax.xaxis.set_minor_locator(fmt_three_months)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%m'))

# Input all event start and end dates
evt_start = dt.datetime.strptime('20191201',"%Y%m%d")
evt_end =  dt.datetime.strptime('20210815',"%Y%m%d")

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

# Calculate change
df['6.2 Hz - 12.5 Hz'] = (df['6.2 Hz - 12.5 Hz'] - base_median)/abs(base_median)*100

# Compute rolling average
df["avg_7"] = df.rolling(window = '7D', on = 'time')['6.2 Hz - 12.5 Hz'].median()
df["avg_3"] = df.rolling(window = '3D', on = 'time')['6.2 Hz - 12.5 Hz'].median()
df["avg_1"] = df.rolling(window = '1D', on = 'time')['6.2 Hz - 12.5 Hz'].median()


# Find average base on date
for avg in ['avg_1','avg_3','avg_7']:
    temp = df.groupby([df['time'].dt.date])[avg].mean().reset_index()
    output_df = output_df.set_index('time').join(temp.set_index('time')).reset_index()

# Remove unusable data
output_df.at[[0,1,2,3,4,5,6],"avg_7"] = np.nan
output_df.at[[0,1,2],"avg_3"] = np.nan

print('NA: ',sum(output_df['avg_1'].isna()))
print('Length: ',len(output_df['avg_1']))
print(output_df)

# Descreptive Stats
mean = np.nanmean(output_df["avg_1"])
std = np.nanstd(output_df["avg_1"])


# df.loc[(df['avg_7'] < mean-2*std) | (df['avg_7']>mean+2*std), "avg_7"] = np.nan
# df.loc[(df['avg_3'] < mean-2*std) | (df['avg_3']>mean+2*std), "avg_3"] = np.nan
# df.loc[(df['avg_1'] < mean-2*std) | (df['avg_1']>mean+2*std), "avg_1"] = np.nan
#print(df['time'].dtype)

# Set plot boundary
ax.set_ylim([mean-3*std, mean+3*std])

# print tails to check
print("Last 20 values: ",df.tail(10))

# Plot
plt.xlabel("Date",fontsize=18)
plt.ylabel("Change (%)",fontsize=18)

# Draw line at lockdown
ax.axvline(dt.datetime.strptime("20210515","%Y%m%d"), color = "red", label = "Taipei lockdown")
ax.axvline(dt.datetime.strptime("20210519","%Y%m%d"), color = "blue", label = "Taiwan lockdown")

# Plot three avg ines
output_df['time'] = pd.to_datetime(output_df['time'])
plt.plot(output_df['time'],output_df["avg_1"], label = "daily avg")
plt.plot(output_df['time'],output_df["avg_3"], label = "3-day avg")
plt.plot(output_df['time'],output_df["avg_7"], label = "7-day avg")

# Plot title and legend
plt.title(f"{Station} PSD Average")
plt.legend()
# plt.show()

# Save fig
OutFigName = 'PNG/'+Station+'_PSD_avg.png'
SavePath = os.path.join(OutFigPath,OutFigName)
fig.savefig(OutFigName)
# fig.savefig(SavePath)

# Save csv
CSV_full_file = 'CSV/'+Station + '_avg_'+start_basedate+'base.csv'
CSV_full_path = os.path.join(OutCSVPath,CSV_full_file)
output_df.to_csv(CSV_full_file)
# output_df.to_csv(CSV_full_path)


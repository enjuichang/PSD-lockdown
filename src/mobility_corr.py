#!/usr/bin/python
import pandas as pd
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import re
import datetime as dt

# Input Path
FileDir = "./CSV/"
OutFigPath = './PNG'
# FileName = sys.argv[1]
FileName = "LDU_avg.csv"

# Input paramters
AppleName = "applemobilitytrends-2021-08-21.csv"
GoogleName = "google_Taiwan.csv"
start_time = '2021-01-01'
end_time = '2021-08-01'
region = 'Kaohsiung City'
trans_type = 'transit'

# RE to parse station name
sta_compiler= re.compile(r'([A-Z]+(\d+)?)')
Station = sta_compiler.findall(FileName)[0][0]
FilePath = os.path.join(FileDir,FileName)

### Parse apple data
def parse_apple(apple,region,trans_type):
    '''
    Inputs:
    - apple (pd.df): raw apple mobility data
    - region (str): name of region of interest (region in Apple's DB)
    - trans_type (str): name of transporatation type (transporatation_type in Apple's DB)

    Outputs:
    new_df (pd.df): converted data to usable pandas dataframe:
        - time (datetime64): time by day
        - val (float64): val by day
    '''

    # Select data
    city = apple[apple.region == region]
    city_trans = city[city.transportation_type == trans_type].transpose()[6:]

    # Process time
    city_trans.index = pd.to_datetime(city_trans.index)
    time = city_trans.index.tolist()

    # Process values
    city_index = city[city.transportation_type == trans_type].index[0]
    val = city_trans[city_index].to_numpy()

    # Create new df
    new_df = pd.DataFrame({'time': time, 'apple': val})
    new_df["apple"] = pd.to_numeric(new_df["apple"], errors='coerce')

    # Find median and normalize val
    median_apple = new_df.set_index('time')['2021-01-03':'2021-02-03']['apple'].median()
    new_df["apple"] = (new_df["apple"] - median_apple)/median_apple*100

    return new_df

# Import data
# df = pd.read_csv('CSV/KAU_avg.csv', dtype={'avg_7': np.float64,  'avg_3': np.float64})#.drop(columns='Unnamed: 0')
df = pd.read_csv(FilePath, dtype={'avg_7': np.float64,  'avg_3': np.float64}).drop(columns='Unnamed: 0')
df["time"] = pd.to_datetime(df["time"])
print(df)
### Apple data preprocess
ApplePath = os.path.join(FileDir,AppleName)
apple = pd.read_csv(ApplePath)

# parse apple data
apple_parsed = parse_apple(apple,region,trans_type)


### Google data preprocess
GooglePath = os.path.join(FileDir,GoogleName)
google_raw_df = pd.read_csv(GooglePath)
google = pd.DataFrame({'time': google_raw_df.date, 'google': google_raw_df.transit_stations_percent_change_from_baseline})
google['time'] = pd.to_datetime(google.time)


# Join dfs
df = df.set_index('time').join(apple_parsed.set_index('time')).reset_index('time')
df = df.set_index('time').join(google.set_index('time')).reset_index('time')

### Output dfs

# Paths and names
AppleOutName = 'apple_'+Station+'_processed.csv'
GoogleOutName = 'google_processed.csv'
AppleOutPath = os.path.join(FileDir,FileName)
GoogleOutPath = os.path.join(FileDir,FileName)

# Output df
df_apple_output = df.set_index('time')['2020-01-13':].reset_index('time')
df_apple_output.to_csv(AppleOutPath, index=False, columns = ['time','apple'])

df_google_output = df.set_index('time')['2020-02-15':].reset_index('time')
df_google_output.to_csv(GoogleOutPath, index=False, columns = ['time','google'])

### Correlation 
# Select time
df_time_selected = df.set_index('time')[start_time:end_time]

# Find Pearson's correlation
apple_corr = df_time_selected.apple.corr(df_time_selected.avg_1)
google_corr = df_time_selected.google.corr(df_time_selected.avg_1)

### Plot
fig, ax1 = plt.subplots()

# Plot google and apple
color = 'tab:red'
ax1.plot(df_time_selected.reset_index()['time'],df_time_selected['apple'], color=color, label = f'Apple (r = {apple_corr:.3f})')
ax1.plot(df_time_selected.reset_index()['time'],df_time_selected['google'], color="Green", label = f'Google (r = {google_corr:.3f})')
ax1.set_ylabel('Change (%)', color=color)
ax1.tick_params(axis='y', labelcolor=color)

# Plot station values
ax2 = ax1.twinx()
color = 'tab:blue'
ax2.plot(df_time_selected.reset_index()['time'],df_time_selected['avg_1'], color=color, label = f'{Station} Daily Average')
ax2.set_ylabel('Change (%)', color=color)  # we already handled the x-label with ax1
ax2.tick_params(axis='y', labelcolor=color)

# Draw line at lockdown
plt.axvline(dt.datetime.strptime("20210515","%Y%m%d"), color = "red", label = "Taipei lockdown")
plt.axvline(dt.datetime.strptime("20210519","%Y%m%d"), color = "blue", label = "Taiwan lockdown")

plt.title(f"Mobility change at {Station}")
fig.legend()
fig.tight_layout()  # otherwise the right y-label is slightly clipped
#plt.show()

# Save fig
OutFigName = Station+'_mobility.png'
SavePath = os.path.join(OutFigPath,OutFigName)
plt.savefig(SavePath)

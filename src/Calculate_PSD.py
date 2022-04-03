#!/usr/bin/python
import os
import pandas as pd
import numpy as np
import obspy
from obspy.io.xseed import Parser
from obspy.signal import PPSD
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import sys
import datetime as dt
import re

# Only in VSCode \\ change
# from glob import glob

# Load data \\ change
Station = sys.argv[1]
# Station = 'TAP'

# ms_dir = sorted(glob("ms_Data/HSN_DATA/*"))
MainPath = './'
RESP_Path = './RESP'
OutFigPath = './PNG'
OutCSVPath = './CSV'
Component = ['HHZ','HLZ','HNZ']
subscript = ''

DataFile = str(Station)+'_2021'
DataPath = os.path.join(MainPath,DataFile)
msLIST = open(DataPath).read().split("\n")[:-1]


# Testing
# msLIST = ["ms_Data/CWB24_20210518.ms","ms_Data/CWB24_20210519.ms","ms_Data/CWB24_20210520.ms","ms_Data/CWB24_20210521.ms"]
# msLIST = [ms for ms in ms_dir]
# period_ls = [1/9,1/11]

# Run input periods
raw_period_ls = sys.argv[2].split(",")
period_ls = []
for per in raw_period_ls:
   raw = per.split("/")
   period_ls.append(float(raw[0])/float(raw[1]))

### Create df and timestamp list
# Input start/end/step
extract_date = re.compile(r'20\d+')
interval = 30
evt_start = dt.datetime.strptime(extract_date.findall(msLIST[0])[0],"%Y%m%d")
evt_end =  dt.datetime.strptime(extract_date.findall(msLIST[-1])[0],"%Y%m%d")
step = dt.timedelta(minutes = interval)

# Storage for PSD
left_freq = [np.nan for i in range(len(period_ls))]
right_freq = [np.nan for i in range(len(period_ls))]
PSD_ls = np.array([[] for i in range(len(period_ls))])
time_ls = np.array([])

# Create df 
PSD_timels = np.array([evt_start])
time_count = evt_start
while time_count < (evt_end+dt.timedelta(days=1)):
    time_count += step
    if time_count.time() != dt.datetime.strptime("23:00", "%H:%M").time() and time_count.time() != dt.datetime.strptime("23:30", "%H:%M").time():
        PSD_timels = np.append(PSD_timels, time_count)
df = pd.DataFrame(PSD_timels, columns = ["time"])

### Round datetime function
def roundTime(time):
    time += dt.timedelta(minutes=15)
    time -= dt.timedelta(minutes=time.minute % 30,seconds=time.second,microseconds=time.microsecond)
    return time

### Find Channel
def channelExtract(ch_ls):
    channels = ["HHZ","HLZ","HNZ"]
    locations = ["10","00"]
    ch_loc = np.asarray([[i+j for j in locations] for i in channels]).flatten()
    found_ch = set(ch_loc).intersection(set(ch_ls))
    if found_ch: return found_ch.pop()
    # Select preference
    elif len(found_ch)>1: 
        for ch in found_ch:
            if ch[:3] == "HHZ": return ch
            elif ch[:3] == "HLZ": ch_curr = ch
            else: ch_curr = ch
        return ch_curr
    # If channel+location doesn't match
    else: raise ValueError("Channel Not Found")


### Iterate through every miniseed
for ms in msLIST:
    st = obspy.Stream()
    st.clear()

    try:
        # Read Data
        DataPath = ms
        WF = obspy.read(DataPath)
    
        # Interpolate missing data
        WF.merge(method=1,fill_value='interpolate')
        #WF = WF.select(location = location)
    
        ### Find all channels, choose channel, and enable RESP
        # Find all channels
        ch_ls = []
        for tr in WF: ch_ls.append(tr.stats.channel+tr.stats.location)
        ch_loc = channelExtract(ch_ls)
        location = ch_loc[3:]
        DIREC = ch_loc[:3]
        WF = WF.select(channel = DIREC)    
        WF = WF.select(location = location)
        tr = WF[0]
        print(tr)

        # Append channel to stream
        st.append(tr)
    
        # Response file upload
        RESP_Name = 'RESP.TW.'+str(Station)+'.'+location+'.'+DIREC
        RESP_File = os.path.join(RESP_Path,RESP_Name)
        print(RESP_File)

	# Parse the response file
        parser = Parser(RESP_File)
        # parser = Parser(RESP_Name)

        ### Creat PPSD instance and join instance to df
        # Create PPSD instance
        ppsd = PPSD(tr.stats,metadata=parser,overlap=0.5)
        # Assign db bin size
        ppsd.db_bins = (-120,-80, 1.0)
        # Add stream
        ppsd.add(st)

        # add storage
        psd_storage = [[] for i in range(len(period_ls))]

        # Join instance to df
        for i, period_cen in enumerate(period_ls):
    
            psd_values = ppsd.extract_psd_values(period_cen)
            psd_storage[i]= psd_values[0]
            left_freq[i] = 1/psd_values[3]
            right_freq[i] = 1/psd_values[1]
        PSD_ls = np.hstack((PSD_ls,np.array(psd_storage)))
    
        # Find timestamps
        time = [i.datetime for i in ppsd.times_processed]
        time_ls = np.concatenate((time_ls,time))
    except:
        pass

### Postprocesses
# Set frequency names
freq_names = [f"{left_freq[i]:.1f} Hz - {right_freq[i]:.1f} Hz" for i in range(len(period_ls))]
# Create time dataframe
time_df = pd.DataFrame(time_ls, columns = ['time'])
time_df = time_df.applymap(lambda x: roundTime(x))
# Create psd dataframe joined by time
psd = time_df.join(pd.DataFrame(PSD_ls.T, columns=freq_names))
# Join output dataframe with psd dataframe
df = df.join(psd.set_index('time'), on = 'time')

# Draw plot
fig, ax = plt.subplots(figsize=(50,20))

print(PSD_ls)

# Find mean and standard deviation
mean = sum([np.nanmean(psd) for psd in PSD_ls])/len(PSD_ls)
std = sum([np.nanstd(psd) for psd in PSD_ls])/len(PSD_ls)

# Get color maps
blues = matplotlib.cm.get_cmap("Blues")
reds = matplotlib.cm.get_cmap("Reds")
len_colors = 0.75/len(period_ls)

# Draw line for each frequency
for i, psd in enumerate(freq_names):
    ax.plot(df['time'], df[psd], color = reds(1-len_colors*i), label = f"PSD ({left_freq[i]:.1f}-{right_freq[i]:.1f} Hz)")

# Format date
# Major ticks every 6 months.
fmt_half_month = mdates.DayLocator(interval=15)
ax.xaxis.set_major_locator(fmt_half_month)

# Minor ticks every month.
fmt_three_days = mdates.DayLocator(interval = 3)
ax.xaxis.set_minor_locator(fmt_three_days)

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))

# Set y limit
ax.set_ylim([mean-3*std, mean+3*std])

plt.xlabel("Date",fontsize=18)
plt.ylabel("Amplitude [$m^2/s^4/Hz$] [dB]",fontsize=18)
plt.title(f"PSD of {DIREC} at {Station} in {left_freq[i]:.1f}-{right_freq[i]:.1f} Hz", fontsize=32)
ax.legend()
# plt.show()

#Save figure name
OutFigName = Station+'_'+DIREC+'_PSD_'+subscript+'.png'
SavePath = os.path.join(OutFigPath,OutFigName)
fig.savefig(SavePath)

CSV_full_file = Station + "_full.csv"
CSV_full_path = os.path.join(OutCSVPath,CSV_full_file)
df.to_csv(CSV_full_path)

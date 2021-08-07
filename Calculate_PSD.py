#!/usr/bin/python
import os
import numpy as np
from glob import glob
import obspy
from obspy.io.xseed import Parser
from obspy.signal import PPSD
# from matplotlib import *
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import time

# Only in VSCode \\ change
#from glob import glob

# Load data \\ change
#Station = sys.argv[1]

ms_dir = sorted(glob("ms_Data/*"))
MainPath = './'
RESP_Path = './'
OutFigPath = './'
DIREC = 'HLZ'
subscript = 'tst'




Station = "TPE" #\\ change

msLIST = ["ms_Data/CWB24_20210517.ms","ms_Data/CWB24_20210518.ms","ms_Data/CWB24_20210519.ms","ms_Data/CWB24_20210520.ms","ms_Data/CWB24_20210521.ms"]
#msLIST = [ms for ms in ms_dir]

# Select periods included
#period_ls = [1/5,1/7,1/9,1/11,1/13]
period_ls = [1/9]
left_freq = [[] for i in range(len(period_ls))]
right_freq = [[] for i in range(len(period_ls))]

PSD_ls = [[] for i in range(len(period_ls))]
PSD_timels = []
PSD_avg_timels = []
PSD_avg_ls = [[] for i in range(len(period_ls))]

start = time.time()

for ms in msLIST:

    psd_time = [[] for i in range(len(period_ls))]
    st = obspy.Stream()
    st.clear()

    # File form Concatenate.sh
    DataFile = str(Station)+'_2021'
    # RESP files
    RESP_Name = 'RESP.TW.'+str(Station)+'.10.'+DIREC
    RESP_File = os.path.join(RESP_Path,RESP_Name)

    # Create data path \\ change
    #DataPath = os.path.join(MainPath,DataFile)
    DataPath = ms

    # Read data
    WF = obspy.read(DataPath)
    # Interpolate missing data
    WF.merge(method=1,fill_value='interpolate')
    WF.sort(keys=['channel'])

    # Choose channel
    tr = WF[2]
    print(tr)
    # Append channel to stream
    st.append(tr)
    # Parse the response file \\ change
    #parser = Parser(RESP_File)  
    parser = Parser("RESP.TW.TAP.10.HLZ")

    # Create PPSD instance
    ppsd = PPSD(tr.stats,metadata=parser,overlap=0.5)
    day_length = 23*ppsd.ppsd_length/3600/ppsd.overlap
    # print(ppsd.psd_values)
    ppsd.db_bins = (-110,-80, 1.0)
    #print(ppsd.db_bins)
    # Add stream
    ppsd.add(st)



    #     # Save figure name
    #     OutFigName = Station+'_'+DIREC+'_PSD_'+subscript+'.png'
    #     SavePath = os.path.join(OutFigPath,OutFigName)
    #     # Return psd values at 0.1 period

    # Deal with PSD values

    for i, period_cen in enumerate(period_ls):
        psd_values = ppsd.extract_psd_values(period_cen)
        psd_time[i] = psd_values[0]
        left_freq[i] = 1/psd_values[3]
        right_freq[i] = 1/psd_values[1]
        #print(timels,"\n")

        # Deal with data gaps
        if len(psd_time[i]) != day_length:
            fill_na = day_length-len(psd_time[i])
            for j in range(int(fill_na)): psd_time[i].append(np.nan)
            PSD_avg_ls[i].append(np.nan)

        # Calculate average PSD per day
        else:
            psd_time_avg = sum(psd_time[i])/len(psd_time[i])
            PSD_avg_ls[i].append(psd_time_avg)
    
        PSD_ls[i] = np.concatenate((PSD_ls[i],psd_time[i]))
    
    # Deal with time
    timels = ppsd.times_processed
    
    # Deal with time data gaps
    if len(timels) != day_length:
        fill_na = day_length-len(timels)
        # Add 30 mins timestamps when no data
        for j in range(int(fill_na)): timels.append(timels[-1]+23/day_length*3600*(j+1))
    PSD_avg_timels.append(timels[0])
    PSD_timels = np.concatenate((PSD_timels,timels))

#fig, (ax0, ax1) = plt.subplots(2,1,figsize=(20,20))
fig, ax = plt.subplots(figsize=(50,20))

PSD_timels = list(map(lambda x: x.matplotlib_date,PSD_timels))
PSD_avg_timels = list(map(lambda x: x.matplotlib_date,PSD_avg_timels))

blues = matplotlib.cm.get_cmap("Blues")
reds = matplotlib.cm.get_cmap("Reds")
len_colors = 0.75/len(period_ls)
#ax0.plot(PSD_timels,PSD_ls)
#ax1.plot(PSD_avg_timels,PSD_avg_ls)
for i, psd in enumerate(PSD_ls):
    ax.plot(PSD_timels, psd, color = reds(1-len_colors*i), label = f"PSD ({left_freq[i]:.1f}-{right_freq[i]:.1f} Hz)")
    ax.plot(PSD_avg_timels,PSD_avg_ls[i], color = blues(1-len_colors*i), label = f"Daily Avg ({left_freq[i]:.1f}-{right_freq[i]:.1f} Hz)")

# Major ticks every 6 months.
fmt_half_month = mdates.DayLocator(interval=15)
# ax0.xaxis.set_major_locator(fmt_half_month)
# ax1.xaxis.set_major_locator(fmt_half_month)
ax.xaxis.set_major_locator(fmt_half_month)

# Minor ticks every month.
fmt_three_days = mdates.DayLocator(interval = 3)
# ax0.xaxis.set_minor_locator(fmt_three_days)
# ax1.xaxis.set_minor_locator(fmt_three_days)
ax.xaxis.set_minor_locator(fmt_three_days)

# Text in the x axis will be displayed in 'YYYY-mm' format.
# ax0.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
# ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

# ax0.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
# ax1.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))

ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

ax.xaxis.set_minor_formatter(mdates.DateFormatter('%d'))
ax.set_ylim([-110, -80])

plt.xlabel("Date",fontsize=18)
plt.ylabel("Amplitude [$m^2/s^4/Hz$] [dB]",fontsize=18)

ax.legend()
fig.show()
fig.savefig("output.png")

output_ls = [PSD_timels]
output_avg_ls = [PSD_avg_timels]
output_name = ["time"]
output_avg_name = ["Avg Time"]

for i in range(len(PSD_ls)):
    output_ls.append(PSD_ls[i])
    output_avg_ls.append(PSD_avg_ls[i])
    output_name.append(f"{left_freq[i]:.1f}-{right_freq[i]:.1f} Hz")


full = pd.DataFrame(output_ls).transpose()
full.columns = output_name
avg = pd.DataFrame(output_avg_ls).transpose()
avg.columns = output_name

print(full)
print(avg)

end = time.time()
print(end-start)
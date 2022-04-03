import os
import sys
import obspy as ob
import numpy as np
import re
import datetime as dt


# Input & Testing
FileName = sys.argv[1]
#FileName = "NHDH_20210529_20210801.mseed"


# RE parsing
station = re.compile(r'([A-Z]+(\d+)?)')
sta = station.findall(FileName)[0][0]

time = re.compile(r'\d+')
stime = time.findall(FileName)[0]
etime = time.findall(FileName)[1]

# ### Path setting ### 

MainPath = "./"
FileDir = "./ms_uncut/"
OutPath = "./ms_DATA/"

evtlst = []


### Define data range from event list
def daterange(d1, d2):
    return (d1 + dt.timedelta(days=i) for i in range((d2 - d1).days + 2))

for d in daterange(dt.datetime.strptime(stime, "%Y%m%d"),dt.datetime.strptime(etime, "%Y%m%d")):
     evtlst.append(d.strftime("%Y%m%d"))


FilePath = os.path.join(FileDir,FileName)

print(FilePath)

# Read file
WF = ob.read(FilePath)
#WF = ob.read(FileName)
print(WF)

for i, evt in enumerate(evtlst):
     if i == 0: start_date = evt
     else:
          # Update end date
          end_date = evt

          ### Waveform cutting ###
          CutWFtime1 = start_date                 # Cut waveform for plotting
          CutWFtime2 = end_date                 # Cut waveform for plotting

          # cut date
          CUTtime1_p = ob.UTCDateTime(CutWFtime1)  # Cut wavefrom for processing
          CUTtime2_p = ob.UTCDateTime(CutWFtime2)  # Cut waveform for processing

          ### Make copy ###
          print('Cut Waveform ..., from '+ str(CUTtime1_p) +" to "+ str(CUTtime2_p))
          untrim_WF = WF.copy()
          
          # Trim
          WF.trim(CUTtime1_p,CUTtime2_p)

          # Output

          OutName = f"CWB24_{sta}_{start_date}.ms"
          SavePath = os.path.join(OutPath,OutName)
          #SavePath = f"ms_cut_output/{OutName}"
          WF.write(SavePath, format = "MSEED")

          # Register copy
          WF = untrim_WF

          # Update start date
          start_date = end_date
          


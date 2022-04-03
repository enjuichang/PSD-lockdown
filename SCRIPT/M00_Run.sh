#!/bin/sh

# Download obspy
#pip install obspy

dates=./EVTLST/evtlst
stalst=./STALST/stalst_n_edit
periods=$(cat ./periods)

for i in $(cat $stalst) # delete $( | grep...)
do
rm $i'_2021'
for day in $(cat $dates) # julian day
do
month=$(date -d $day +%m)
jday=$(date -d $day +%j)

echo ./ms_DATA/CWB24_${i}_${day}.ms >> ${i}_2021 # Change month

done

python ./src/Calculate_PSD.py $i $periods
rm ${i}_2021
done

for sta in $(cat $stalst)
do
python ./src/draw_avg.py ${sta}_full.csv
done 
python ./src/multi_station.py $stalst
exit


#!/bin/sh

# Download obspy
#pip install obspy

#dates=./EVTLST/evtlst_tst
dates=./EVTLST/evtlst_191201_210815
#stalst=stalst
stalst=$1
#stalst=./STALST/stalst_n_edit

for i in $(cat $stalst) # delete $( | grep...)
do
rm $i'_2021'
for day in $(cat $dates) # julian day
do
month=$(date -d $day +%m)
jday=$(date -d $day +%j)

echo ./ms_DATA/CWB24_${i}_${day}.ms >> ${i}_2021 # Change month
done

python ./src/spectogram_draw.py $i

rm ${i}_2021
done


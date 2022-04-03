#!/bin/sh


stalst=$1
#stalst=./STALST/stalst_n_edit

for sta in $(cat $stalst)
do 
python ./src/draw_avg.py ${sta}_full.csv
done

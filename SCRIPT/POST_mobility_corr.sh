#!/bin/sh

stalst=$1

for sta in $(cat $stalst)
do
python src/mobility_corr.py ${sta}_avg.csv
done
exit

#!/bin/sh

stalst=./STALST/stalst_new

for((i=1;i<=$(cat $stalst | wc -l);i++))
do
if (( $i == 1 ))
then
curr_num=0
awk -v row="$i" 'FNR == row {print $1}' $stalst >> STALST/stalst${curr_num}
elif (( $i % 4 == 0 ))
then
awk -v row="$i" 'FNR == row {print $1}' $stalst >> STALST/stalst${curr_num}
curr_num=$i
else
awk -v row="$i" 'FNR == row {print $1}' $stalst >> STALST/stalst${curr_num}
fi
done

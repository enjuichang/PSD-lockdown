#!/bin/sh
#'''
#Generate a list of dates between start_date and end_date
#'''

start_date="2021-01-01"
end_date="2021-08-15"
output_name="210101_210815"

until [[ $start_date > $end_date ]]; do 
    format=$(date -d $start_date +%Y%m%d)
    echo "$format" >> ../EVTLST/evtlst_${output_name}
    start_date=$(date -I -d "$start_date + 1 day")
  
done





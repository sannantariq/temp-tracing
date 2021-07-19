#!/bin/bash

DST=$1
EXP_NAME=$2

temp_ss_input="${EXP_NAME}_raw.txt"
temp_ss_output="${EXP_NAME}_ss.txt"
temp_stat_output="${EXP_NAME}_stats.txt"

cleanup ()
{
    cat $temp_ss_input |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked" > $temp_ss_output
	exit 0
}

trap cleanup SIGINT SIGTERM

while [ 1 ]; do 
	ss --no-header -ein dst $DST | ts '%.s' | tee -a $temp_ss_input
	sudo tc -s class show dev lo | ts '%.s' | sed -e ':a; /$/ { N; s/\n/|/; ba; }' | sed  -e 's/[0-9]\+.[0-9]\+\s|/\n/g' -e 's/|[0-9]\+.[0-9]\+\||//g' >> $temp_stat_output
	sudo tc -s qdisc show dev lo | ts '%.s' | sed -e ':a; /$/ { N; s/\n/|/; ba; }' | sed -e 's/|\([0-9]\+.[0-9]\+\)\sqdisc/\n\1 qdisc/g' -e 's/|[0-9]\+.[0-9]\+\||//g' >> $temp_stat_output

done

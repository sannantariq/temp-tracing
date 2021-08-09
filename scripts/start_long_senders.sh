#!/usr/bin/env bash

START=$1
END=$2
DST=$3
TIME=$4
ALGO=$5

if [ $START -gt $END ]
then
    echo "Invalid START and END values"
    exit 0
fi



for ((i=$START;i<=$END;i++)); do
    if [ "$ALGO" = "bbr" ]
    then
        echo "Running Command: iperf3 -c ${DST} -p ${i} -C 'bbr' -t ${TIME} >> /dev/null &"
        iperf3 -c $DST -p $i -C 'bbr' -t $TIME >> /dev/null &
    else
        echo "Running Command: iperf3 -c ${DST} -p ${i} -C 'cubic' -t ${TIME} >> /dev/null &"
        iperf3 -c $DST -p $i -C 'cubic' -t $TIME >> /dev/null &
    fi
done
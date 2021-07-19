#!/usr/bin/env bash

START=$1
END=$2

if [ $START -gt $END ]
then
    echo "Invalid START and END values"
    exit 0
fi

for ((i=$START;i<=$END;i++)); do
    echo "Running command iperf3 -s -p ${i}"
    iperf3 -s -p $i &
done
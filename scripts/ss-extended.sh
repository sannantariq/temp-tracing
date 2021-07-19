#!/bin/bash

DST=$1

touch sender-ss-extended.txt

rm -f sender-ss-extended.txt 

cleanup ()
{
	# get timestamp
	ts=$(cat sender-ss-extended.txt |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked" |  awk '{print $1}')

	# get sender
	sender=$(cat sender-ss-extended.txt |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  | grep "unacked" | awk '{print $6}')


	# retransmissions - current, total
	retr=$(cat sender-ss-extended.txt |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  | grep "unacked" |  grep -oP '\bretrans:.*\brcv_space'  | awk -F '[:/ ]' '{print $2","$3}' | tr -d ' ')


	# get cwnd, ssthresh
	cwn=$(cat sender-ss-extended.txt |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"    |  grep "unacked" | grep -oP '\bcwnd:.*(\s|$)\bbytes_acked' | awk -F '[: ]' '{print $2","$4}')

	# get rtt
	rtt=$(cat sender-ss-extended.txt |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  | grep "unacked" |  grep -oP '\brtt:.*\/'  | awk -F '[:/ ]' '{print $2}')

	# get minrtt
	minrtt=$(cat sender-ss-extended.txt |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  | grep "unacked" |  grep -oP '\bminrtt:.*(\s|$)'  | awk -F '[: ]' '{print $2}')

	# concatenate into one CSV
	paste -d ',' <(printf %s "$ts") <(printf %s "$sender") <(printf %s "$retr") <(printf %s "$cwn") <(printf %s "$rtt") <(printf %s "$minrtt") > sender-ss-extended.csv

	exit 0
}

trap cleanup SIGINT SIGTERM

while [ 1 ]; do 
	ss --no-header -ein dst $DST | ts '%.s' | tee -a sender-ss-extended.txt 
done

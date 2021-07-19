#!/bin/bash


INPUT_FILE_PATH=$1
OUTPUT_FILE_PATH=$2

cleanup ()
{
    # relevant_text=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked")
	# get timestamp
    # echo $relevant_text
	ts=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked"| awk '{print $1}')

	# get sender
	sender=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked"| awk '{print $5}')

    # get receiver
    recvr=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked" | awk '{print $6}')


	# retransmissions - current, total
    ret_current=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked"|  grep -oP '\bretrans:.*\brcv_space'  | awk -F '[:/ ]' '{print $2}')
	ret_total=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked"|  grep -oP '\bretrans:.*\brcv_space'  | awk -F '[:/ ]' '{print $3}')


	# get cwnd, ssthresh
	cwn=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked" | grep -oP '\bcwnd:.*(\s|$)' | awk -F '[: ]' '{print $2}')
    ssthresh=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked"| grep -oP '\bbytes_acked:.*(\s|$)' | awk -F '[: ]' '{print $2}')

	# get rtt
	rtt=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked"|  grep -oP '\brtt:.*\/'  | awk -F '[:/ ]' '{print $2}')

	# get minrtt
	minrtt=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked" |  grep -oP '\bminrtt:.*(\s|$)'  | awk -F '[: ]' '{print $2}')

    # get data packets out
    data_segs_out=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked" |  grep -oP '\bdata_segs_out:.*(\s|$)'  | awk -F '[: ]' '{print $2}')

    # get_cc_algo
    cc=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB"  |  grep "unacked" |  grep -oP '(\bcubic|\breno|\bbbr|\bvegas)\s' | awk '{print $1}')

	# concatenate into one CSV
	paste -d ',' <(printf %s "$ts") <(printf %s "$sender") <(printf %s "$recvr") <(printf %s "$ret_current") <(printf %s "$ret_total") <(printf %s "$cwn") <(printf %s "$ssthresh") <(printf %s "$rtt") <(printf %s "$minrtt") <(printf %s "$data_segs_out") <(printf %s "$cc") > $OUTPUT_FILE_PATH

	exit 0
}



# relevant_text=$(cat $INPUT_FILE_PATH |   sed -e ':a; /<->$/ { N; s/<->\n//; ba; }' | grep "tcpESTAB" | grep "unacked")
# echo $relevant_text > $OUTPUT_FILE_PATH
# ts=$(echo "$relevant_text" | awk '{print $1}')

# # get sender
# sender=$(echo "$relevant_text" | awk '{print $5}')

# # get receiver
# recvr=$(echo "$relevant_text" | awk '{print $6}')

# cwn=$(echo "$relevant_text" | grep -oP '\bcwnd:.*(\s|$)\bbytes_acked' | awk -F '[: ]' '{print $2}')

# paste -d ',' <(printf %s "$ts") <(printf %s "$sender") <(printf %s "$recvr") <(printf %s "$cwn") > $OUTPUT_FILE_PATH

cleanup
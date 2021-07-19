#!/usr/bin/env bash

interface='lo'


# add_qdisc_netem parent_handle handle delay buffer_size 
add_qdisc_netem () {
    sudo tc qdisc add dev $interface parent $1 handle $2 netem delay $3 limit $4
}


# add_qdisc_htb parent_handle handle default_class
add_qdisc_htb () {
    sudo tc qdisc add dev $interface parent $1 handle $2 htb default $3
}

# add_class_htb parent class_id rate ceil burst
add_class_htb() {
    sudo tc class add dev $interface parent $1 classid $2 htb rate $3 ceil $4 burst $5
}

# add_filter_dport parent prio port_number port_mask flow_id
add_filter_dport() {
    sudo tc filter add dev $interface protocol ip parent $1 prio $2 u32 match ip dport $3 $4 flowid $5
}


# assign correct mtu
sudo ip link set dev $interface mtu 1500

# create root htb qdisc
add_qdisc_htb "root" "1:" "30"

# create sub classes
add_class_htb "1:" "1:1" "10mbit" "10mbit" "3k"
add_class_htb "1:1" "1:30" "2mbit" "2mbit" "3k"
add_class_htb "1:1" "1:10" "4mbit" "8mbit" "3k"
add_class_htb "1:1" "1:20" "4mbit" "8mbit" "3k"

# add delay leaf queues
add_qdisc_netem "1:10" "10:" "100ms" "500"
add_qdisc_netem "1:20" "20:" "100ms" "500"

# add filters
add_filter_dport "1:0" "1" "5000" "0xfff0" "1:10"
add_filter_dport "1:0" "2" "6000" "0xfff0" "1:20"
#!/usr/bin/env python3

import subprocess
import sys
import time
import queue
from concurrent.futures import ThreadPoolExecutor as Pool


INFO = {
    'dst_ip': '128.95.190.53',
    'min_port': 5601,
    'max_port': 5617,
    'cc_algo': 'bbr',
    'duration': 40,
    'flows': [
        {
            'flow_name': 'big_mouse',
            'quantity': 1,
            'predelay': 0.5,
            'postdelay': 0.5,
            'length_type': 'time',
            'length': 20,
        },
        {
            'flow_name': 'medium_mouse',
            'quantity': 5,
            'predelay': 0.5,
            'postdelay': 0.5,
            'length_type': 'time',
            'length': 5,
        },
        {
            'flow_name': 'little_mouse',
            'quantity': 10,
            'predelay': 0.5,
            'postdelay': 0.5,
            'length_type': 'time',
            'length': 2,
        },
    ]
}

class SenderFlow:
    def __init__(self, flow_size, pre_delay, post_delay, mode='size'):
        self.pre_delay = pre_delay
        self.post_delay = post_delay
        self.mode = mode
        if mode == "size":
            self.flow_size = flow_size
        elif mode == "time":
            self.flow_time = flow_size

    def get_cmd(self, dst_ip, port, cc_algo):
        if self.mode == "size":
            cmd = f"iperf3 -c {dst_ip} -p {port} -C '{cc_algo}' -n {self.flow_size}"
        elif self.mode == "time":
            cmd = f"iperf3 -c {dst_ip} -p {port} -C '{cc_algo}' -t {self.flow_time}"
        return cmd


class PoolQueue:
    def __init__(self, port_list, cc_algo, dst_ip):
        self.cc_algo = cc_algo
        self.dst_ip = dst_ip
        self.port_queue = queue.Queue()
        for p in port_list:
            self.port_queue.put(p)

        self.pool = Pool(max_workers=len(port_list))

    def add_port(self, port):
        self.port_queue.put(port)

    def get_port(self):
        return self.port_queue.get()

    def run_flow(self, sender_flow):
        port = self.get_port()
        cmd = sender_flow.get_cmd(self.dst_ip, port, self.cc_algo)
        print(f"Running {cmd}")
        # f = self.pool.submit(subprocess.run, [f'sleep {sender_flow.pre_delay};echo "running cmd with {cmd}";sleep {sender_flow.post_delay};'])
        f = self.pool.submit(subprocess.run, [f'sleep {sender_flow.pre_delay};{cmd};sleep {sender_flow.post_delay};'], shell=True)
        f.add_done_callback(lambda future: self.add_port(port))
    
    def shutdown(self):
        self.pool.shutdown(wait=False)


def main():

    min_port = INFO['min_port']
    max_port = INFO['max_port']
    dst_ip = INFO['dst_ip']
    cc_algo = INFO['cc_algo']
    total_test_time = INFO['duration']

    port_list = list(range(min_port, max_port + 1))


    
    sender_flows = []

    for flow in INFO['flows']:
        mode = flow['length_type']
        length = flow['length']
        predelay = flow['predelay']
        postdelay = flow['postdelay']

        for _ in range(flow['quantity']):
            sender_flows.append(SenderFlow(length, predelay, postdelay, mode=mode))

    
    pool = PoolQueue(port_list, cc_algo, dst_ip)

    start_time = time.time()
    i = 0
    while time.time() - start_time < total_test_time:
        pool.run_flow(sender_flows[i])
        i = (i + 1) % len(sender_flows)
    
    pool.shutdown()




if __name__ == "__main__":
    main()
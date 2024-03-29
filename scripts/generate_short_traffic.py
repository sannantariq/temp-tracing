#!/usr/bin/env python3

import subprocess
import sys
import time
import queue
from concurrent.futures import ThreadPoolExecutor as Pool
from threading import Lock


class LogName:
    def __init__(self, logfile_prefix, baseval=0):
        self.logfile_prefix = logfile_prefix
        self.val = baseval
        self.lock = Lock()

    def get(self):
        with self.lock:
            self.val += 1
            return f"{self.logfile_prefix}/{self.val}.json"
            
class SenderFlow:
    def __init__(self, flow_size, pre_delay, post_delay, log_name_generator, mode='size'):
        self.pre_delay = pre_delay
        self.post_delay = post_delay
        self.log_name_generator = log_name_generator
        self.mode = mode
        if mode == "size":
            self.flow_size = flow_size
        elif mode == "time":
            self.flow_time = flow_size

    def get_cmd(self, dst_ip, port, cc_algo):
        if self.mode == "size":
            cmd = f"iperf3 -c {dst_ip} -p {port} -C '{cc_algo}' -n {self.flow_size} -J --logfile {self.log_name_generator.get()}"
        elif self.mode == "time":
            cmd = f"iperf3 -c {dst_ip} -p {port} -C '{cc_algo}' -t {self.flow_time} -J --logfile {self.log_name_generator.get()}"
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


def get_logfile_name(logfile_prefix):
    c = Counter()
    return f"{logfile_prefix}/{c.get()}.json"

def main():
    if len(sys.argv) < 10:
        print(f"Usage: {__file__} min_port max_port dst_ip cc_algo total_test_time avg_flow_size[-time] avg_predelay avg_postdelay logfile_prefix")
        sys.exit(0)

    min_port = int(sys.argv[1])
    max_port = int(sys.argv[2])
    dst_ip = sys.argv[3]
    cc_algo = sys.argv[4]
    total_test_time = float(sys.argv[5])
    avg_flow_size = int(sys.argv[6])
    avg_predelay = float(sys.argv[7])
    avg_postdelay = float(sys.argv[8])
    logfile_prefix = sys.argv[9]

    port_list = list(range(min_port, max_port + 1))

    log_gen = LogName(logfile_prefix)


    mode = 'size'
    if avg_flow_size < 0:
        mode = 'time'

    # sender_flows = []
    # for _ in range(2):
    #     sender_flows.append()
    sender_flows = [SenderFlow(abs(avg_flow_size), avg_predelay, avg_postdelay, log_gen, mode=mode)]
    
    pool = PoolQueue(port_list, cc_algo, dst_ip)

    start_time = time.time()
    i = 0
    while time.time() - start_time < total_test_time:
        pool.run_flow(sender_flows[i])
        i = (i + 1) % len(sender_flows)
    
    pool.shutdown()


    

    # port_queue = queue.Queue()
    # for p in range(min_port, max_port + 1):
    #     port_queue.put(p)

    # procs = Pool(max_workers=5)

    # def make_addback_callback(p):
    #     def add_back_callback(future):
    #         if future.exception():
    #             print("there was an exception!!")
    #         else:
    #             port_queue.put(p)
    #     return add_back_callback
        


    # start_time = time.time()
    # while time.time() - start_time < total_test_time:
    #     port = port_queue.get()
    #     print(f"acquired {port}")
    #     time.sleep(per_flow_delay)
    #     # cmd = ['iperf3', '-c', dst_ip, '-p', f"{port}", '-C', f"'{cc_algo}'", "-t", f"{per_flow_time}"]
    #     cmd = f"iperf3 -c {dst_ip} -p {port} -C '{cc_algo}' -t {per_flow_time}"
    #     f = procs.submit(subprocess.run, [cmd], shell=True)
    #     f.add_done_callback(make_addback_callback(port))
        

    # procs.shutdown(wait=False)






if __name__ == "__main__":
    main()
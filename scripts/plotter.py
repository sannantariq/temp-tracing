import pandas as pd
import numpy as np 
from gnuplotter.plotter.plot2d import Plot, create_dataset
import sys
import re
from csv import DictWriter

def plot(plot_data, outfilepath, underlays=[], return_dataset_only=False):
    
    datasets = []
    datasets.append(create_dataset(plot_data['time'], plot_data['cwnd'], with_='linespoints', axes='x1y1', title='cwnd'))
    datasets.append(create_dataset(plot_data['time'], plot_data['rtt'], with_='linespoints', axes='x1y2', title='rtt'))

    if not return_dataset_only:
        p = Plot("tcp_stats", outfilepath)
        
        for u in underlays:
            p.push_dataset(u)
        for d in datasets:
            p.push_dataset(d)
        
        cmds = ['set y2label "rtt(ms)"', 'set ytics nomirror', 'set y2tics 100', 'set key outside above']
        p.plot('', x_label='time', y_label='cwnd(mss)', custom_cmds=cmds)
    return datasets

def plot_qdata(plot_data, outfilepath, underlays=[], return_dataset_only=False):
    
    datasets = []
    datasets.append(create_dataset(plot_data['time'], plot_data['backlog_pkts'], with_='linespoints', title='pkts'))

    if not return_dataset_only:
        p = Plot("tcp_stats", outfilepath)
        
        for u in underlays:
            p.push_dataset(u)
        for d in datasets:
            p.push_dataset(d)
        
        cmds = ['set key outside above']
        p.plot('', x_label='time', y_label='packets in queue', custom_cmds=cmds)
    return datasets

def get_printable_name(addr):
    print(f"Pulling apart address: {addr}")
    addr = addr.split(':')
    addr, port = ''.join(addr[:-1]), addr[-1]
    addr = addr.replace('[', '').replace(']', '').replace(':', '').replace('.', '_')
    
    return f"{addr}_{port}"
        
def process_tcp_ss_line(line, regex_dict):
    # print("Processing:-", line)
    def process_match(txt, field_name, pattern, converter):
        match = pattern.search(txt)
        if match:
            return converter(match.group(field_name))
        else:
            return ''
    
    return {k:process_match(line, k, p, converter) for k, (p, converter) in regex_dict.items()}




def process_tcp_ss_file(filename):
    regexes = {
        'time' : (r"(?P<time>^\d+\.\d+)", lambda x: float(x)),
        'sender': (r"^\S+\s+\S+\s+\S+\s+\S+\s+(?P<sender>\S+)", lambda x: str(x)),
        'recvr': (r"^\S+\s+\S+\s+\S+\s+\S+\s+\S+\s+(?P<recvr>\S+)", lambda x: str(x)),
        'ret_current': (r"retrans:(?P<ret_current>\d+)", lambda x: int(x)),
        'ret_total': (r"retrans:\d+/(?P<ret_total>\d+)", lambda x: int(x)),
        'cwnd': (r"cwnd:(?P<cwnd>\d+)", lambda x: int(x)),
        'ssthresh': (r"\sssthresh:(?P<ssthresh>\d+)", lambda x: int(x)),
        'rtt': (r"\srtt:(?P<rtt>\d+\.\d+|\d+)", lambda x: float(x)),
        'minrtt': (r"\sminrtt:(?P<minrtt>\d+\.\d+|\d+)", lambda x: float(x)),
        'data_segs_out': (r"\sdata_segs_out:(?P<data_segs_out>\d+)", lambda x: int(x)),
        'cc': (r"\s(?P<cc>cubic|vegas|bbr|reno)\s", lambda x: str(x)),
    }

    regexes = {k:(re.compile(pattern), converter) for k, (pattern, converter) in regexes.items()}

    raw = None
    with open(filename, 'r') as f:
        raw = f.readlines()
    
    res = [process_tcp_ss_line(line, regexes) for line in raw]
    return res
    

def get_tcp_ss(filename):
    df = pd.DataFrame(data=process_tcp_ss_file(filename))
    return df


def process_qstats_line(line, regex_dict):
    # print(f"Processing line:{line}")
    def process_match(txt, field_name, pattern, converter):
        return converter(pattern.search(txt).group(field_name))

    return {k:process_match(line, k, p, converter) for k, (p, converter) in regex_dict.items()}


def process_qstats_file(filename):
    regexes = {
        'time' : (r"(?P<time>^\d+\.\d+)", lambda x: float(x)),
        'rectype': (r"^\S+\s(?P<rectype>\S+)", lambda x: str(x)),
        'qtype': (r"(qdisc|class)\s(?P<qtype>\w+)", lambda x: str(x)),
        'qid': (r"(qdisc|class)\s\w+\s(?P<qid>\S+)", lambda x: str(x)),
        'sent_bytes': (r"\sSent\s(?P<sent_bytes>\d+)\sbytes", lambda x: int(x)),
        'sent_pkts': (r"\sSent\s\d+\sbytes\s(?P<sent_pkts>\d+)\spkt", lambda x: int(x)),
        'dropped': (r"dropped\s(?P<dropped>\d+)", lambda x: int(x)),
        'backlog_bytes': (r"\sbacklog\s(?P<backlog_bytes>\d+)\w*b", lambda x: str(x)),
        'backlog_pkts': (r"\sbacklog\s\d+\w*b\s(?P<backlog_pkts>\d+)p", lambda x: int(x))
    }

    regexes = {k:(re.compile(pattern), converter) for k, (pattern, converter) in regexes.items()}

    raw = None
    with open(filename, 'r') as f:
        raw = f.readlines()

    res = [process_qstats_line(line, regexes) for line in raw if 'Sent' in line]
    return res


def get_qstats(filename):
    df = pd.DataFrame(data=process_qstats_file(filename))
    return df

# def main():
#     filename = "/Users/stariq/Documents/Research/lossVdelay/tracing/scripts/bbrq_stats.txt"
#     df = get_qstats(filename)
#     print(df.head())

def main():
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} exp_name output_folder_path")
        sys.exit(0)
    exp_name= sys.argv[1]
    outfile_prefix = sys.argv[2]
    
    tcp_data = get_tcp_ss(exp_name + '_ss.txt')
    tcp_data = tcp_data.fillna(0)

    start_time = tcp_data['time'].iloc[0]
    tcp_data['time'] -= start_time
    

    addr_pairs = tcp_data[['sender', 'recvr']]

    sender_pairs = addr_pairs.drop_duplicates()
    print(sender_pairs)
    for _, row in sender_pairs.iterrows():
        s_addr, r_addr = row['sender'], row['recvr']
        sender_data = tcp_data[(tcp_data.sender.eq(s_addr) & tcp_data.recvr.eq(r_addr))]

        # skip spurious connections
        if sender_data.shape[0] < 50:
            continue

        outfile_path = f"{outfile_prefix}/{get_printable_name(s_addr)}_{get_printable_name(r_addr)}"
        plot(sender_data, outfile_path)

    qdata = get_qstats(exp_name + "_stats.txt")
    qdata['time'] -= start_time
    # print(qdata.head())
    # print(start_time)

    queues = qdata[['rectype', 'qtype', 'qid']]
    queues = queues.drop_duplicates()

    for _, row in queues.iterrows():
        rectype, qtype, qid = row['rectype'], row['qtype'], row['qid']

        queue_data = qdata[(qdata.time.ge(0)) & (qdata.rectype.eq(rectype)) & (qdata.qtype.eq(qtype)) & (qdata.qid.eq(qid))]
        # print(queue_data.head())

        outfile_path = f"{outfile_prefix}/{rectype}_{qtype}_{qid}"
        plot_qdata(queue_data, outfile_path)


if __name__ == "__main__":
    main()
    # print(get_printable_name('[::ffff:127.0.0.1]:5201'))
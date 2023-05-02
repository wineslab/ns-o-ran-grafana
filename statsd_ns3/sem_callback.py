import csv
from typing import Dict, List, Set, Tuple
import numpy as np
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer
import threading
import time
from statsd import StatsClient
import re

lock = threading.Lock()


class SimWatcher(PatternMatchingEventHandler):
    """
    Watchdog event handler for each simulation

    """
    patterns = ['cu-up-cell-1.txt', 'cu-cp-cell-*.txt', "du-cell-*.txt"]
    kpm_map: Dict[Tuple[int, int], List] = {}
    consumed_keys: Set[Tuple[int, int]]
    telegraf_host = "localhost"
    telegraf_port = 8125

    def __init__(self):
        PatternMatchingEventHandler.__init__(self, patterns=self.patterns,
                                             ignore_patterns=['cu-cp-cell-1.txt'],
                                             ignore_directories=True, case_sensitive=False)
        self.directory = ''
        self.consumed_keys = set()

    def on_created(self, event):
        super().on_created(event)

    def on_modified(self, event):
        super().on_modified(event)
        # print(event.src_path)

        lock.acquire()
        with open(event.src_path, 'r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                timestamp = int(row['timestamp'])
                ue_imsi = int(row['ueImsiComplete'])
                ue = row['ueImsiComplete']
                key = (timestamp, ue_imsi)
                if key not in self.consumed_keys:

                    if re.search('cu-up-cell-[1-5].txt', file.name):
                        if key not in self.kpm_map:
                            self.kpm_map[key] = []

                        for column_name in reader.fieldnames:
                            if row[column_name] == '':
                                continue
                            self.kpm_map[key].append(float(row[column_name]))

                        self.consumed_keys.add(key)
                        self.send_to_telegraf_up(ue=ue, values=self.kpm_map[key])

                    if re.search('cu-cp-cell-[2-5].txt', file.name):
                        if key not in self.kpm_map:
                            self.kpm_map[key] = []

                        for column_name in reader.fieldnames:
                            if row[column_name] == '':
                                continue
                            self.kpm_map[key].append(float(row[column_name]))

                        self.consumed_keys.add(key)
                        self.send_to_telegraf_cp(ue=ue, values=self.kpm_map[key])

                    if re.search('du-cell-[2-5].txt', file.name):
                        if key not in self.kpm_map:
                            self.kpm_map[key] = []

                        for column_name in reader.fieldnames:
                            if row[column_name] == '':
                                continue
                            self.kpm_map[key].append(float(row[column_name]))

                        self.consumed_keys.add(key)
                        self.send_to_telegraf_du(ue=ue, values=self.kpm_map[key])

        lock.release()

    def on_closed(self, event):
        super().on_closed(event)

    def send_to_telegraf_up(self, ue, values):
        # connect to Telegraf
        statsd_client = StatsClient(self.telegraf_host, self.telegraf_port, prefix = None)

        # send data to telegraf

        # convert timestamp in nanoseconds (InfluxDB)
        timestamp = int(values[0]*(pow(10,6))) # int because of starlark
        pdcp_latency = values[7]*(pow(10, -1))

        pipe = statsd_client.pipeline()

        stat_avg_lat = 'avg_latency_' + ue
        pipe.gauge(stat=stat_avg_lat, value = values[2], tags={'timestamp':timestamp})

        stat_cellDlTxVolume = 'tx_volume_' + ue
        pipe.gauge(stat=stat_cellDlTxVolume, value=values[4], tags={'timestamp':timestamp})

        stat_tx = 'tx_bytes_' + ue
        pipe.gauge(stat=stat_tx, value=values[5], tags={'timestamp':timestamp})

        stat_txDlPackets = 'tx_packets_' + ue
        pipe.gauge(stat=stat_txDlPackets, value=values[6], tags={'timestamp':timestamp})

        stat_pdcp_throughput = 'pdcp_throughput_' + ue
        pipe.gauge(stat=stat_pdcp_throughput, value=values[7], tags={'timestamp':timestamp})

        stat_pdcp_latency = 'pdcp_latency_' + ue
        pipe.gauge(stat=stat_pdcp_latency, value=pdcp_latency, tags={'timestamp':timestamp})
        
        pipe.send()

    def send_to_telegraf_cp(self, ue, values):

        statsd_client = StatsClient(self.telegraf_host, self.telegraf_port, prefix = None)

        # convert timestamp in nanoseconds (InfluxDB)
        timestamp = int(values[0]*(pow(10,6))) # int because of starlark


    def send_to_telegraf_du(self, ue, values):

        statsd_client = StatsClient(self.telegraf_host, self.telegraf_port, prefix = None)

        # convert timestamp in nanoseconds (InfluxDB)
        timestamp = int(values[0]*(pow(10,6))) # int because of starlark


if __name__ == "__main__":
    event_handler = SimWatcher()
    observer = Observer()
    observer.schedule(event_handler, ".", False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()




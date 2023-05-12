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
    patterns = ['cu-up-cell-*.txt', 'cu-cp-cell-*.txt', "du-cell-*.txt"]
    kpm_map: Dict[Tuple[int, int, int], List] = {}
    consumed_keys: Set[Tuple[int, int]]
    telegraf_host = "localhost"
    telegraf_port = 8125
    statsd_client = StatsClient(telegraf_host, telegraf_port, prefix = None)

    def __init__(self):
        PatternMatchingEventHandler.__init__(self, patterns=self.patterns,
                                             ignore_patterns=[],
                                             ignore_directories=True, case_sensitive=False)
        self.directory = ''
        self.consumed_keys = set()

    def on_created(self, event):
        super().on_created(event)

    def on_modified(self, event):
        super().on_modified(event)

        lock.acquire()
        with open(event.src_path, 'r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                timestamp = int(row['timestamp'])
                ue_imsi = int(row['ueImsiComplete'])
                ue = row['ueImsiComplete']
                
                if re.search('cu-up-cell-[2-5].txt', file.name):
                    key = (timestamp, ue_imsi, 0)
                if re.search('cu-cp-cell-[2-5].txt', file.name):
                    key = (timestamp, ue_imsi, 1)
                if re.search('du-cell-[1-5].txt', file.name):
                    key = (timestamp, ue_imsi, 2)
                if  file.name == './cu-up-cell-1.txt':
                    key = (timestamp, ue_imsi, 3)   # to see data for eNB cell
                if file.name == './cu-cp-cell-1.txt':
                    key = (timestamp, ue_imsi, 4)   # same here


                if key not in self.consumed_keys:

                    if key not in self.kpm_map:
                        self.kpm_map[key] = []

                    fields = []

                    for column_name in reader.fieldnames:
                        if row[column_name] == '':
                            continue
                        self.kpm_map[key].append(float(row[column_name]))
                        fields.append(column_name)

                    regex = re.search(r"\w*-(\d+)\.txt", file.name)
                    fields.append('file_id_number')
                    self.kpm_map[key].append(regex.group(1))

                    self.consumed_keys.add(key)
                    self.send_to_telegraf(ue=ue, values=self.kpm_map[key], fields=fields, file_type=key[2])

        lock.release()

    def on_closed(self, event):
        super().on_closed(event)

    def send_to_telegraf(self, ue, values, fields, file_type):
        
        # send data to telegraf
        pipe = self.statsd_client.pipeline()

        # convert timestamp in nanoseconds (InfluxDB)
        timestamp = int(values[0]*(pow(10,6))) # int because of starlark
        
        # convert pdcp_latency, SHOULD BE DONE WITH ''''' if field == 'pdcp_lat...
        if file_type==3:
            values[7] = values[7]*(pow(10, -1))

        i = 0
        for field in fields:

            if field == 'file_id_number':
                continue

            if field == 'DRB.PdcpSduDelayDl (cellAverageLatency)':
                stat = 'DRB.PdcpSduDelayDl (cellAverageLatency)_cell_' + values[-1]
                stat = stat.replace(' ','')
                pipe.gauge(stat=stat, value=values[i], tags={'timestamp':timestamp})
                i+=1
                continue

            if field == 'm_pDCPBytesDL (cellDlTxVolume)':
                stat = 'm_pDCPBytesDL (cellDlTxVolume)_cell_' + values[-1]
                stat = stat.replace(' ','')
                pipe.gauge(stat=stat, value=values[i], tags={'timestamp':timestamp})
                i+=1
                continue

            if field == 'numActiveUes':
                stat = 'numActiveUes_cell_' + values[-1]
                pipe.gauge(stat=stat, value=values[i], tags={'timestamp':timestamp})
                i+=1
                continue

            stat = field + '_' + ue
            if file_type == 0 or file_type == 3:
                stat += '_up'
            if file_type == 1 or file_type == 4:
                stat += '_cp'
            if file_type == 2:
                stat += '_du'
            stat = stat.replace(' ','')
            pipe.gauge(stat=stat, value = values[i], tags={'timestamp':timestamp})
            i+=1
        pipe.send()


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




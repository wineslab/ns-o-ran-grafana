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
    kpm_map: Dict[Tuple[int, int, int], List] = {}
    consumed_keys: Set[Tuple[int, int]]
    telegraf_host = "localhost"
    telegraf_port = 8125
    statsd_client = StatsClient(telegraf_host, telegraf_port, prefix = None)

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

        lock.acquire()
        with open(event.src_path, 'r') as file:
            reader = csv.DictReader(file)

            for row in reader:
                timestamp = int(row['timestamp'])
                ue_imsi = int(row['ueImsiComplete'])
                ue = row['ueImsiComplete']
                
                if re.search('cu-up-cell-[1-5].txt', file.name):
                    key = (timestamp, ue_imsi, 0)
                if re.search('cu-cp-cell-[2-5].txt', file.name):
                    key = (timestamp, ue_imsi, 1)
                if re.search('du-cell-[2-5].txt', file.name):
                    key = (timestamp, ue_imsi, 2)


                if key not in self.consumed_keys:

                    if re.search('cu-up-cell-[1-5].txt', file.name):
                        if key not in self.kpm_map:
                            self.kpm_map[key] = []

                        fields = []

                        for column_name in reader.fieldnames:
                            if row[column_name] == '':
                                continue
                            self.kpm_map[key].append(float(row[column_name]))
                            fields.append(column_name)

                        self.consumed_keys.add(key)
                        self.send_to_telegraf_up(ue=ue, values=self.kpm_map[key], fields=fields)

                    if re.search('cu-cp-cell-[2-5].txt', file.name):
                        if key not in self.kpm_map:
                            self.kpm_map[key] = []

                        fields = []

                        for column_name in reader.fieldnames:
                            if row[column_name] == '':
                                continue
                            self.kpm_map[key].append(float(row[column_name]))
                            fields.append(column_name)

                        self.consumed_keys.add(key)
                        self.send_to_telegraf_cp(ue=ue, values=self.kpm_map[key], fields=fields)

                    if re.search('du-cell-[2-5].txt', file.name):
                        if key not in self.kpm_map:
                            self.kpm_map[key] = []

                        fields = []

                        for column_name in reader.fieldnames:
                            if row[column_name] == '':
                                continue
                            self.kpm_map[key].append(float(row[column_name]))
                            fields.append(column_name)

                        self.consumed_keys.add(key)
                        self.send_to_telegraf_du(ue=ue, values=self.kpm_map[key], fields=fields)

        lock.release()

    def on_closed(self, event):
        super().on_closed(event)

    def send_to_telegraf_up(self, ue, values, fields):
        
        # send data to telegraf
        pipe = self.statsd_client.pipeline()

        # convert timestamp in nanoseconds (InfluxDB)
        timestamp = int(values[0]*(pow(10,6))) # int because of starlark
        values[7] = values[7]*(pow(10, -1))

        i = 0
        for field in fields:
            stat = field + '_' + ue + '_up'
            stat = stat.replace(' ','')
            pipe.gauge(stat=stat, value = values[i], tags={'timestamp':timestamp})
            i+=1
        pipe.send()

    def send_to_telegraf_cp(self, ue, values, fields):
        
        # send data to telegraf
        pipe = self.statsd_client.pipeline()

        # convert timestamp in nanoseconds (InfluxDB)
        timestamp = int(values[0]*(pow(10,6))) # int because of starlark

        i = 0
        for field in fields:
            stat = field + '_' + ue + '_cp'
            stat = stat.replace(' ','')
            pipe.gauge(stat=stat, value = values[i], tags={'timestamp':timestamp})
            i+=1
        pipe.send()

    def send_to_telegraf_du(self, ue, values, fields):
        
        # send data to telegraf
        pipe = self.statsd_client.pipeline()

        # convert timestamp in nanoseconds (InfluxDB)
        timestamp = int(values[0]*(pow(10,6))) # int because of starlark

        i = 0
        for field in fields:
            stat = field + '_' + ue + '_du'
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




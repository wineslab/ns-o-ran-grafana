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
    A Python event handler that looks for specific .txt formatted as csv files, parses data from them, and sends it to Telegraf as part of a watchdog object.

    Attributes
    ----------
    patterns : list
        A list of file patterns that the event handler will monitor.
        
    kpm_map : Dict[Tuple[int, int, int], List]
        A dictionary that contains the data for every measurement in the csv file.
        
    consumed_keys : Set[Tuple[int, int, int]]
        A list of keys already used in the dictionary.
        
    telegraf_host : str
        The host address of the Telegraf server "localhost" by default.
        
    telegraf_port : int
        The port number of the Telegraf server, 8125 by default.
        
    statsd_client : StatsClient
        The StatsD client for sending metrics to Telegraf automatically created by default with the above parameters.

        
    Methods
    -------
    __init__(self)
        Initializes the event handler
        
    on_created(self, event)
        Handles the on_created event triggered when a new file is created.
        
    on_closed(self, event)
        Handles the on_closed event triggered when a file is closed.
        
    on_modified(self, event)
        Handles the on_modified event triggered when a file is modified.

    send_to_telegraf(self, ue, values, fields, file_type)
        Formats and sends data to the Telegraf agent
    """
 
    patterns = ['cu-up-cell-*.txt', 'cu-cp-cell-*.txt', "du-cell-*.txt"]
    kpm_map: Dict[Tuple[int, int, int], List] = {}
    consumed_keys: Set[Tuple[int, int, int]]
    telegraf_host = "localhost"
    telegraf_port = 8125
    statsd_client = StatsClient(telegraf_host, telegraf_port, prefix = None)

    def __init__(self):

        """
        Initializes the class
        """

        PatternMatchingEventHandler.__init__(self, patterns=self.patterns,
                                             ignore_patterns=[],
                                             ignore_directories=True, case_sensitive=False)
        self.directory = ''
        self.consumed_keys = set()

    def on_created(self, event):

        """
        Handles the on_created event triggered when a new file is created.
        """

        super().on_created(event)

    def on_modified(self, event):

        """
        Handles the on_modified event triggered when a file is modified.
        """

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

                    fields = list()

                    for column_name in reader.fieldnames:
                        if row[column_name] == '':
                            continue
                        self.kpm_map[key].append(float(row[column_name]))
                        fields.append(column_name)

                    regex = re.search(r"\w*-(\d+)\.txt", file.name)
                    fields.append('file_id_number')
                    self.kpm_map[key].append(regex.group(1))      # last item of list will be file_id_number

                    self.consumed_keys.add(key)
                    self._send_to_telegraf(ue=ue, values=self.kpm_map[key], fields=fields, file_type=key[2])

        lock.release()

    def on_closed(self, event):

        """
        Handles the on_closed event triggered when a file is closed.
        """

        super().on_closed(event)

    def _send_to_telegraf(self, ue:int, values:List, fields:List, file_type:int):

        """
        Formats and sends data to the Telegraf agent.

        Parameters
        ----------
        ue : int
            Value extracted from csv, represents the ue.
        values : List
            List of metrics to send to Telegraf.
        fields : List
            List of field names corresponding to the metrics in the values parameter.
        file_type: int
            Ranges from 1 to 3. Represents if the metrics come from a up, cu or du file respectively.

        Notes
        -----
        The "stat" parameter of the gauge() function will then be shown as the table name in InfluxDB, this explains the stat string formatting for each metric.
        """
        
        # send data to telegraf
        pipe = self.statsd_client.pipeline()

        # convert timestamp in nanoseconds (InfluxDB)
        timestamp = int(values[0]*(pow(10,6))) # int because of starlark
        
        i = 0
        for field in fields:

            if field == 'file_id_number':
                continue

            # convert pdcp_latency
            if field == 'DRB.PdcpSduDelayDl.UEID (pdcpLatency)':
                values[i] = values[i]*pow(10, -1)

            if 'UEID' not in field:
                stat = field + '_cell_' + values[-1]
                stat = stat.replace(' ','')
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

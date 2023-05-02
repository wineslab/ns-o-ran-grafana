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

        pipe = statsd_client.pipeline()

        #values[0] is the timestamp
        #values[1] is ueImsiComplete 

        num_active_ues = values[2]
        stat_num_active_ues = 'num_active_ues_' + ue
        pipe.gauge(stat=stat_num_active_ues, value=num_active_ues, tags={'timestamp': timestamp})
        
        numDrb = values[3] #DRB.EstabSucc.5QI.UEID (numDrb)
        stat_numDrb = 'num_drb_' + ue
        pipe.gauge(stat=stat_numDrb, value=numDrb, tags={'timestamp':timestamp})

        #values[4] is DRB.RelActNbr.5QI.UEID (0): all zeros so I ignore it

        L3_serving_Id_m_cellId = values[5]
        stat_L3_serving_Id = "L3_serving_Id_m_cellId_" + ue
        pipe.gauge(stat=stat_L3_serving_Id, value=L3_serving_Id_m_cellId, tags={'timestamp': timestamp})

        #values[6] is UE (imsi), we have it yet

        L3_serving_SINR = values[7]
        stat_L3_serving_SINR = "L3_serving_SINR_" + ue
        pipe.gauge(stat=stat_L3_serving_SINR, value=L3_serving_SINR, tags={'timestamp': timestamp})


        L3_serving_SINR_3gpp = values[8]
        stat_L3_serving_SINR_3gpp = "L3_serving_SINR_3gpp_" + ue
        pipe.gauge(stat=stat_L3_serving_SINR_3gpp, value=L3_serving_SINR_3gpp, tags={'timestamp': timestamp})


        L3_neigh_Id_1_cellId = values[9]
        stat_L3_neigh_Id_1_cellId = "L3_neigh_Id_1_cellId_" + ue
        pipe.gauge(stat=stat_L3_neigh_Id_1_cellId, value=L3_neigh_Id_1_cellId, tags={'timestamp': timestamp})


        stat_L3neighSINR1 = "L3_neigh_SINR1_" + ue
        pipe.gauge(stat=stat_L3neighSINR1, value=values[10], tags={'timestamp': timestamp})


        stat_L3neighSINR3gpp1_convertedSinr = "L3_neigh_SINR_3gpp_1_convertedSinr_" + ue
        pipe.gauge(stat=stat_L3neighSINR3gpp1_convertedSinr, value=values[11], tags={'timestamp': timestamp})


        stat_L3_neigh_Id_2_cellId = "L3_neigh_Id_2_cellId_" + ue
        pipe.gauge(stat=stat_L3_neigh_Id_2_cellId, value=values[12], tags={'timestamp':timestamp})


        stat_L3neighSINR2 = "L3_neigh_SINR_2_" + ue
        pipe.gauge(stat=stat_L3neighSINR2, value=values[13], tags={'timestamp':timestamp})


        stat_L3_neigh_SINR_3gpp_2_convertedSinr = "L3_neigh_SINR_3gpp_2_convertedSinr_" + ue
        pipe.gauge(stat=stat_L3_neigh_SINR_3gpp_2_convertedSinr, value=values[14], tags={'timestamp':timestamp})


        stat_L3neighId3_cellId = "L3neighId3_cellId_" + ue
        pipe.gauge(stat=stat_L3neighId3_cellId, value=values[15], tags={'timestamp':timestamp})


        stat_L3neighSINR3 = "L3_neigh_SINR_3_" + ue
        pipe.gauge(stat=stat_L3neighSINR3, value=values[16], tags={'timestamp':timestamp})


        stat_L3_neigh_SINR_3gpp_3_convertedSinr = "L3_neigh_SINR_3gpp_3_convertedSinr_" + ue
        pipe.gauge(stat=stat_L3_neigh_SINR_3gpp_3_convertedSinr, value=values[17], tags={'timestamp':timestamp})


        stat_L3_neigh_Id_4_cellId = "L3_neigh_Id_4_cellId_" + ue
        pipe.gauge(stat=stat_L3_neigh_Id_4_cellId, value=values[18], tags={'timestamp':timestamp})


        stat_L3neighSINR4 = "L3_neigh_SINR4_" + ue
        pipe.gauge(stat=stat_L3neighSINR4, value=values[19], tags={'timestamp':timestamp})


        stat_L3_neigh_SINR_3gpp_4_convertedSinr = "L3_neigh_SINR_3gpp_4_convertedSinr_" + ue
        pipe.gauge(stat=stat_L3_neigh_SINR_3gpp_4_convertedSinr, value=values[20], tags={'timestamp':timestamp})


        stat_L3neighId5_cellId = "L3_neigh_ Id_5_cellId_" + ue
        pipe.gauge(stat=stat_L3neighId5_cellId, value=values[21], tags={'timestamp':timestamp})


        stat_L3neighSINR5 = "L3neigh_ SINR5_" + ue
        pipe.gauge(stat=stat_L3neighSINR5, value=values[22], tags={'timestamp':timestamp})


        stat_L3neighSINR3gpp5_convertedSinr = "L3neighSINR3gpp5_convertedSinr_" + ue
        pipe.gauge(stat=stat_L3neighSINR3gpp5_convertedSinr, value=values[23], tags={'timestamp': timestamp})


        stat_L3neighId6_cellId = "L3neighId6_cellId_" + ue
        pipe.gauge(stat=stat_L3neighId6_cellId, value=values[24], tags={'timestamp': timestamp})


        stat_L3neighSINR6 = "L3neighSINR6_" + ue
        pipe.gauge(stat=stat_L3neighSINR6, value=values[25], tags={'timestamp': timestamp})


        stat_L3neighSINR3gpp6_convertedSinr = "L3neighSINR3gpp6_convertedSinr_" + ue
        pipe.gauge(stat=stat_L3neighSINR3gpp6_convertedSinr, value=values[26], tags={'timestamp': timestamp})


        stat_L3neighId7_cellId = "L3neighId7_cellId_" + ue
        pipe.gauge(stat=stat_L3neighId7_cellId, value=values[27], tags={'timestamp': timestamp})


        stat_L3neighSINR7 = "L3neighSINR7_" + ue
        pipe.gauge(stat=stat_L3neighSINR7, value=values[28], tags={'timestamp': timestamp})


        stat_L3neighSINR3gpp7_convertedSinr = "L3neighSINR3gpp7_convertedSinr_" + ue
        pipe.gauge(stat=stat_L3neighSINR3gpp7_convertedSinr, value=values[29], tags={'timestamp': timestamp})


        stat_L3neighId8_cellId = "L3neighId8_cellId_" + ue
        pipe.gauge(stat=stat_L3neighId8_cellId, value=values[30], tags={'timestamp': timestamp})


        stat_L3neighSINR8 = "L3neighSINR8_" + ue
        pipe.gauge(stat=stat_L3neighSINR8, value=values[31], tags={'timestamp': timestamp})


        stat_L3neighSINR3gpp8_convertedSinr = "L3neighSINR3gpp8_convertedSinr_" + ue
        pipe.gauge(stat=stat_L3neighSINR3gpp8_convertedSinr, value=values[32], tags={'timestamp': timestamp})

        pipe.send()



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




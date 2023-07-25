import pyshark
import datetime
from math import *
import pandas as pd

# DF SRC (pacchetti inviati da me):	npack_spike	sizepack_spike	freq_spike	npack_game	sizepack_game	freq_game
df_src = pd.DataFrame(columns=['id_cap', 'npack_spike', 'sizepack_spike', 'freq_spike', 'npack_game', 'sizepack_game', 'freq_game'])

# DF DST (pacchetti che ho ricevuto): npack_spike	sizepack_spike	freq_spke	npack_game	sizepack_game	freq_game
df_dst = pd.DataFrame(columns=['id_cap', 'npack_spike', 'sizepack_spike', 'freq_spike', 'npack_game', 'sizepack_game', 'freq_game'])


for i in range(1, 31):

    n_file = str(i) + ".pcap"
    cap = pyshark.FileCapture(n_file)

    #print("cap " + str(i) + ":")
    #print(cap)

    num_pack_src_spike = 0
    size_pack_src_spike = 0
    num_pack_src_game = 0
    size_pack_src_game = 0
    num_pack_dst_spike = 0
    size_pack_dst_spike = 0
    num_pack_dst_game = 0
    size_pack_dst_game = 0

    first_timestamp = -1
    last_timestamp = -1

    for packet in cap:

        if 'ip' in packet:
            
            ip_src = packet.ip.src
            ip_dst = packet.ip.dst

            # inviati da me
            if '192.0.0.0' < ip_src < '193.0.0.0':

                # il traffico che ci interessa
                if '104.0.0.0' < ip_dst < '105.0.0.0':
    
                    timestamp = packet.sniff_time
                
                    if (num_pack_src_spike == 0):
                        first_timestamp = timestamp

                    #primi 2 sec sono spike
                    # print("Timestamp:", timestamp)
                    # print("first_timestamp:", first_timestamp)
                    differenza = timestamp - first_timestamp
                    #print("differenza:" + str(timestamp - first_timestamp)) 

                    due_sec = datetime.timedelta(seconds=2)
                    #print("due sec:", due_sec)
                    if (differenza < due_sec):
                        num_pack_src_spike += 1
                        size_pack_src_spike += int(packet.length) 
                        #print("questo pacchetto fa parte dello spike")
                    else:
                        num_pack_src_game += 1
                        size_pack_src_game += int(packet.length)


            # indirizzati a me 
            if '192.0.0.0' < ip_dst < '193.0.0.0':

                # il traffico che ci interessa
                if '104.0.0.0' < ip_src < '105.0.0.0':

                    timestamp = packet.sniff_time
                    
                    if (num_pack_dst_spike == 0):
                        first_timestamp = timestamp

                    #primi 2 sec sono spike
                    # print("Timestamp:", timestamp)
                    # print("first_timestamp:", first_timestamp)
                    differenza = timestamp - first_timestamp
                    #print("differenza:" + str(timestamp - first_timestamp)) 

                    due_sec = datetime.timedelta(seconds=2)
                    #print("due sec:", due_sec)
                    if (differenza < due_sec):
                        num_pack_dst_spike += 1
                        size_pack_dst_spike += int(packet.length)
                        #print("questo pacchetto fa parte dello spike")
                    else:
                        num_pack_dst_game += 1
                        size_pack_dst_game += int(packet.length)
                    
        # aggiornato continuamente, alla fine avrà effettivamente il timestamp dell'ultimo pacchetto
        last_timestamp = packet.sniff_time
        

    duration = last_timestamp - first_timestamp
 
    secondi_totali = duration.total_seconds()

    print("\t pcap:" + n_file)
    print("\t num_pack_src_spike:" + str(num_pack_src_spike) + ' sizepack_src_spike:' + str(size_pack_src_spike / num_pack_src_spike) + " num_pack_src_game:" + str(num_pack_src_game) + ' sizepack_game:' + str(size_pack_src_game / num_pack_src_game) + " num_pack_dst_spike:" + str(num_pack_dst_spike) + 'sizepack_spike' + str(size_pack_dst_spike / num_pack_dst_spike) + 
    " num_pack_dst_game:" + str(num_pack_dst_game) + ' sizepack_game:' + str(size_pack_dst_game / num_pack_dst_game) + " secondi totali:" + str(secondi_totali))
    print("\n\n")

    data = {'id_cap': i, 'npack_spike': num_pack_src_spike, 'sizepack_spike': size_pack_src_spike / num_pack_src_spike, 'freq_spike': num_pack_src_spike / 2, 'npack_game': num_pack_src_game, 'sizepack_game': size_pack_src_game / num_pack_src_game, 'freq_game': num_pack_src_game / secondi_totali}
    df_src = pd.concat([df_src, pd.DataFrame(data, index=[0])], ignore_index=True)
    data = {'id_cap': i, 'npack_spike': num_pack_dst_spike, 'sizepack_spike': size_pack_dst_spike / num_pack_dst_spike, 'freq_spike': num_pack_dst_spike / 2, 'npack_game': num_pack_dst_game, 'sizepack_game': size_pack_dst_game / num_pack_dst_game, 'freq_game': num_pack_dst_game / secondi_totali}
    df_dst = pd.concat([df_dst, pd.DataFrame(data, index=[0])], ignore_index=True)

    cap.close()


print("df_src:")
print(df_src)
print("df_dst:")
print(df_dst)


src_npack_spike_mean = df_src['npack_spike'].mean()
src_sizepack_spike_mean = df_src['sizepack_spike'].mean()
src_freq_spike_mean = df_src['freq_spike'].mean()

src_npack_game_mean = df_src['npack_game'].mean()
src_sizepack_game_mean = df_src['sizepack_game'].mean()
src_freq_game_mean = df_src['freq_game'].mean()

# metà dello spike dell'inizio
src_npack_end_mean = df_src['npack_spike'].mean() / 2
src_sizepack_end_mean = df_src['sizepack_spike'].mean() / 2
src_freq_end_mean = df_src['freq_spike'].mean() / 2

dst_npack_spike_mean = df_dst['npack_spike'].mean()
dst_sizepack_spike_mean = df_dst['sizepack_spike'].mean()
dst_freq_spike_mean = df_dst['freq_spike'].mean()

dst_npack_game_mean = df_dst['npack_game'].mean()
dst_sizepack_game_mean = df_dst['sizepack_game'].mean()
dst_freq_game_mean = df_dst['freq_game'].mean()

# metà dello spike dell'inizio
dst_npack_end_mean = df_dst['npack_spike'].mean() / 2
dst_sizepack_end_mean = df_dst['sizepack_spike'].mean() / 2
dst_freq_end_mean = df_dst['freq_spike'].mean() / 2



# non approssimati                    
print("\n\n\
 \n numero pacchetti medio spike iniziale (src): " + str(src_npack_spike_mean) +
"\n dimensione media pacchetti spike iniziale (src): " + str(src_sizepack_spike_mean) + " bytes" +   
"\n frequenza media pacchetti spike iniziale (src): " + str(src_freq_spike_mean) + " pacchetti al secondo" + 

"\n numero pacchetti medio game (src): " + str(src_npack_game_mean) + 
"\n dimensione media pacchetti game (src): " + str(src_sizepack_game_mean) + " bytes" + 
"\n frequenza media pacchetti game (src): " + str(src_freq_game_mean) + " pacchetti al secondo" + 

"\n numero pacchetti medio end (src): " + str(src_npack_end_mean) +  
"\n dimensione media pacchetti end (src): " + str(src_sizepack_end_mean) + 
"\n frequenza media pacchetti end (src): " + str(src_freq_end_mean) +

"\n numero pacchetti medio spike iniziale (dst): " + str(dst_npack_spike_mean) + 
"\n dimensione media pacchetti spike iniziale (dst): " + str(dst_sizepack_spike_mean) + " bytes" + 
"\n frequenza media pacchetti spike iniziale (dst): " + str(dst_freq_spike_mean) + " pacchetti al secondo" + 

"\n numero pacchetti medio game (dst): " + str(dst_npack_game_mean) + 
"\n dimensione media pacchetti game (dst): " + str(dst_sizepack_game_mean) + " bytes" + 
"\n frequenza media pacchetti game (dst): " + str(dst_freq_game_mean) + " pacchetti al secondo" + 

"\n numero pacchetti medio end (dst): " + str(dst_npack_end_mean) +  
"\n dimensione media pacchetti end (dst): " + str(dst_sizepack_end_mean) + 
"\n frequenza media pacchetti end (dst): " + str(dst_freq_end_mean) +

"\n\n")


# approssimati
print("\n\n\
 \n\n numero pacchetti medio spike iniziale (src): " + str(ceil(src_npack_spike_mean)) +
"\n\n dimensione media pacchetti spike iniziale (src): " + str(round(src_sizepack_spike_mean)) + " bytes" +   
"\n\n frequenza media pacchetti spike iniziale (src): " + str(ceil(src_freq_spike_mean)) + " pacchetti al secondo" + 

"\n\n numero pacchetti medio game (src): " + str(ceil(src_npack_game_mean)) + 
"\n\n dimensione media pacchetti game (src): " + str(round(src_sizepack_game_mean)) + " bytes" + 
"\n\n frequenza media pacchetti game (src): " + str(ceil(src_freq_game_mean)) + " pacchetti al secondo" + 

"\n\n numero pacchetti medio end (src): " + str(ceil(src_npack_end_mean)) +  
"\n\n dimensione media pacchetti end (src): " + str(round(src_sizepack_end_mean)) + " bytes" + 
"\n\n frequenza media pacchetti end (src): " + str(ceil(src_freq_end_mean)) + " pacchetti al secondo" +

"\n\n numero pacchetti medio spike iniziale (dst): " + str(ceil(dst_npack_spike_mean)) + 
"\n\n dimensione media pacchetti spike iniziale (dst): " + str(round(dst_sizepack_spike_mean)) + " bytes" + 
"\n\n frequenza media pacchetti spike iniziale (dst): " + str(ceil(dst_freq_spike_mean)) + " pacchetti al secondo" + 

"\n\n numero pacchetti medio game (dst): " + str(ceil(dst_npack_game_mean)) + 
"\n\n dimensione media pacchetti game (dst): " + str(round(dst_sizepack_game_mean)) + " bytes" + 
"\n\n frequenza media pacchetti game (dst): " + str(ceil(dst_freq_game_mean)) + " pacchetti al secondo" + 

"\n\n numero pacchetti medio end (dst): " + str(ceil(dst_npack_end_mean)) +  
"\n\n dimensione media pacchetti end (dst): " + str(round(dst_sizepack_end_mean)) + "bytes" +
"\n\n frequenza media pacchetti end (dst): " + str(ceil(dst_freq_end_mean)) + " pacchetti al secondo" +

"\n\n\n")
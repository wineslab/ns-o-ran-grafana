# Graphical Visualization of simulated ns3 data with Grafana

This example showcases graphical data visualization using Grafana. Data is extracted from a 5G ns3 simulation into csv files and sent to an InfluxDB server via Telegraf. Grafana then gathers data and plots it on a dashboard, allowing for easier analysis and interpretation. The demo dashboard we created showcases two metrics, "pdcp_latency" and "tx_bytes," which were generated from the cu-up-cell-1.txt file within the simulation container. However, this is just a small sample of the vast amount of data that is going to be visualized in this way.

## Services and Ports

### Grafana
- URL: http://localhost:3000 
- User: admin 
- Password: admin 

### Telegraf
- Port: 8125 UDP (StatsD input)

### InfluxDB
- Port: 8086 (HTTP API)
- User: admin 
- Password: admin 
- Database: influx

# How to run the project

## Start the stack with docker compose

```bash
$ docker compose up
```

### Open Grafana and select "Demo" dashboard
- URL: http://localhost:3000 
- User: admin 
- Password: admin 

## Run the python script
```bash
$ docker compose exec ns3 /bin/bash
$ cd ns3-mmwave-oran
$ python3 sem_callback.py
```

## Run the ns3 simulation
```bash
$ docker compose exec ns3 /bin/bash
$ cd ns3-mmwave-oran
$ ./waf --run "scratch/scenario-zero.cc --enableE2FileLogging=1"
```

You may want to set the following options in the last command:
1. `--RngRun=n`, where n is a positive integer representing the seed for the pseudo-random number generator.
2. `--simTime=x`, where x is the simulation time (in seconds)


## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.

## Acknowledgements and credits 

https://github.com/bcremer/docker-telegraf-influx-grafana-stack.git

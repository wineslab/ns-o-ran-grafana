# Graphical Visualization of simulated ns3 data with Grafana

This example showcases graphical data visualization using Grafana. Data is extracted from a 5G ns3 simulation into csv files and sent to an InfluxDB server via Telegraf. Grafana then gathers data and plots it on a dashboard, allowing for easier analysis and interpretation. We created four dashboards to showcase all the data generated from "cu-up", "cu-cp" and "du" files within the simulation container. The forth dashboard plots aggregated data of interest.  

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

### Open Grafana and select a dashboard
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

## Usage
Once everything is running correctly make sure the absolute time range on Grafana is set to "Last 5 minutes" so that data will appear as soon as it is sent.  
When data is visible you may want to change the absolute time range to:  
**From**: timestamp of the first visible measurement  
**To**: From timestamp + simulation time

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.

## Acknowledgements and credits 

https://github.com/bcremer/docker-telegraf-influx-grafana-stack.git

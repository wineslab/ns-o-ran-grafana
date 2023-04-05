# Example Docker Compose project for Telegraf, InfluxDB and Grafana

This an example project to show the TIG (Telegraf, InfluxDB and Grafana) stack.

![Example Screenshot](./example.png?raw=true "Example Screenshot")

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
$ docker compose exec ns3 /bin/sh
$ cd ns3-mmwave-oran
$ python3 sem_callback.py
```

## Run the ns3 simulation
```bash
$ docker compose exec ns3 /bin/sh
$ cd ns3-mmwave-oran
$ ./waf --run "scratch/scenario-zero.cc --enableE2FileLogging=1"
```

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.

## Acknowledgements and credits 

https://github.com/bcremer/docker-telegraf-influx-grafana-stack.git

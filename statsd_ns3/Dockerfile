FROM wineslab/o-ran-sc-bldr-ubuntu18-c-go:9-u18.04 as buildenv
ARG log_level_e2sim=2
# log_level_e2sim = 0 ->  LOG_LEVEL_UNCOND   0
# log_level_e2sim = 1 -> LOG_LEVEL_ERROR     1
# log_level_e2sim = 2 -> LOG_LEVEL_INFO      2
# log_level_e2sim = 3 -> LOG_LEVEL_DEBUG     3

# Install E2sim
RUN mkdir -p /workspace
RUN apt-get update && apt-get install -y build-essential git cmake libsctp-dev autoconf automake libtool bison flex libboost-all-dev

WORKDIR /workspace

RUN git clone -b develop https://github.com/wineslab/ns-o-ran-e2-sim /workspace/e2sim

RUN mkdir /workspace/e2sim/e2sim/build
WORKDIR /workspace/e2sim/e2sim/build
RUN cmake .. -DDEV_PKG=1 -DLOG_LEVEL=${log_level_e2sim}

RUN make package
RUN echo "Going to install e2sim-dev"
RUN dpkg --install ./e2sim-dev_1.0.0_amd64.deb
RUN ldconfig

WORKDIR /workspace

# Install ns-3
RUN apt-get install -y g++ python3 python3-pip

RUN git clone -b release https://github.com/wineslab/ns-o-ran-ns3-mmwave /workspace/ns3-mmwave-oran
RUN git clone -b master https://github.com/o-ran-sc/sim-ns3-o-ran-e2 /workspace/ns3-mmwave-oran/contrib/oran-interface

WORKDIR /workspace/ns3-mmwave-oran

RUN ./waf configure --enable-tests --enable-examples
RUN ./waf build

WORKDIR /workspace

# Install dependencies for script

RUN pip3 install statsd joblib numpy watchdog statsd-tags
RUN pip3 install statsd-telegraf --user
COPY sim_watcher.py /workspace/ns3-mmwave-oran/

WORKDIR /workspace


CMD [ "/bin/sh" ]

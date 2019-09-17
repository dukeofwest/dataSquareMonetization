FROM python:3.7-buster as base

# base image layer
FROM base as builder

WORKDIR /tmp
RUN mkdir /install
COPY requirements.txt .
RUN python3 -m pip install --prefix=/install --no-warn-script-location -r requirements.txt

# application layer
FROM base

ENV PYTHONUNBUFFERED=1

COPY --from=builder /install /usr/local

RUN apt-get update && \
    apt-get -y install sumo && \
    rm -rf /var/lib/apt/lists/*

ENV SUMO_HOME /usr/share/sumo
ENV PYTHONPATH /usr/share/sumo/tools

ENV XBR_DEBUG_NETWORK_ADDR 0x254dffcd3277c0b1660f6d42efbb754edababc2b
ENV XBR_DEBUG_TOKEN_ADDR 0xcfeb869f69431e42cdb54a4f4f105c19c080a601

ENV FLEET_SIM_TYPE poi

WORKDIR /app
COPY README.md .
COPY cfg cfg
COPY fleet-simulation fleet-simulation

ENTRYPOINT ["python3", "-m", "fleet-simulation"]
CMD ["cfg/FFM.sumo.cfg"]

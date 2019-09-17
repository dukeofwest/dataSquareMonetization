# Vehicle Fleet Simulation

SUMO powered fleet simulation that publishes some status information via WAMP.

## Dependencies:

* Python >3.5. This project uses asyncio. Currently it is only tested with Python 3.7.
* [SUMO](https://sumo.dlr.de/wiki/Simulation_of_Urban_MObility_-_Wiki) (EPL v2)
* [autobahn-python](https://github.com/crossbario/autobahn-python) (MIT)

## Quickstart

### With docker

* Run `docker build -t fleet-simulation .` to build the docker container
* Run `docker run -d -e FLEET_SIM_URL=<crossbar router URL> fleet-simulation`

### Native for development

Optional (but highly recommended):
* Create a virtual environment with `virtualenv -p python3 venv`
* Enable the virtual env `source venv/bin/activate`

Required:
* Install SUMO. Description can be found in [sumo-generator/README.md](sumo-generator/README.md)
* Install the python dependencies via `pip install -r requirements.txt`
* Run with `python -m fleet-simulation <config.sumo.cfg>`

## Configuration

A SUMO configuration is needed to run this service. Take an existing one from the `cfg` folder or look at
[sumo-generator/README.md](sumo-generator/README.md) for steps to create one.

This service can be configured via environment variables or command line parameters.
If both are set for the same setting the command line parameter takes precedence.
The following parameters are available:

| command line parameter | environment variable   | default                | description                  |
|------------------------|------------------------|------------------------|------------------------------|
| -n, --name             | FLEET_SIM_NAME         | sumo                   | name of the simulated fleet  |
| --type                 | FLEET_SIM_TYPE         | gps                    | fleet simulation type        |
| -k, --privkey          | FLEET_SIM_PRIVKEY      |                        | Private key used for seller  |
| -u, --url              | FLEET_SIM_URL          | ws://localhost:8080/ws | WAMP router URL              |
| -r, --realm            | FLEET_SIM_REALM        | realm1                 | WAMP realm                   |
| -o, --role             | FLEET_SIM_ROLE         | anonymous              | WAMP role                    |
| -i, --id               | FLEET_SIM_ID           |                        | user ID                      |
| -t, --ticket           | FLEET_SIM_TICKET       |                        | authentication ticket        |

## Published data

The fleet simulation publishes data about events that happen while the simulation is run on WAMP.
Each vehicle of the simulation has its own topics it will publish on.
The format of the topics is `com.conti.hackathon.<name>.<id>.<event>`.

If the `--privkey` option is provided or the `FLEET_SIM_PRIVKEY` environment variable is set the simulation will encrypt the data before publishing.

The `<name>` part can be set when starting the simulation and can be used to differentiate between multiple running simulations.

The `<id>` part is unique for each vehicle in the simulation.
Currently it is implemented as `sha256(<name> + <id_from_sumo>)`.

Different simulation types will publish on or more `<event>` types.
Currently the following events will be published:

| event    | simulation type | description                       |
|----------|-----------------|-----------------------------------|
| position | gps, parking    | current GPS position              |
| parking  | parking         | GPS of detected free parking spot |
| poi      | poi             | position and type of detected POI |

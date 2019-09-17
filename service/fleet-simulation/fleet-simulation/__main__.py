#!/usr/bin/env python3

# Copyright (c) 2019 Continental Automotive GmbH
#
# Alle Rechte vorbehalten. All Rights Reserved.
# The reproduction, transmission or use of this document or its contents is
# not permitted without express written authority.
# Offenders will be liable for damages. All rights, including rights created
# by patent grant or registration of a utility model or design, are reserved.

"""Vehicle Fleet Simulation.

SUMO powered fleet simulation that publishes some status information via WAMP.
"""

import argparse
import asyncio
import binascii
import os
import time
import xml.etree.ElementTree as ET

from hashlib import sha256
from uuid import UUID

import traci
import traci.constants as TC

from autobahn.asyncio.component import Component
from autobahn.asyncio.component import run
from autobahn.asyncio.xbr import SimpleSeller
from autobahn.wamp import PublishOptions

DEBUG_ENABLED = True
DEBUG_ACK_SEND = False

DEFAULT_URL = "ws://localhost:8080/ws"
DEFAULT_REALM = "realm1"
DEFAULT_ROLE = "anonymous"
DEFAULT_SIMU_NAME = "sumo"

WAMP_TOPIC_PREFIX = "com.conti.hackathon"


class WampPublisher:
    """Wrapper class for WAMP publish that just publishes."""
    def __init__(self):
        pass

    async def on_join(self, session):
        pass

    async def publish(self, session, topic, payload):
        if DEBUG_ACK_SEND:
            pub = await session.publish(topic, payload, options=PublishOptions(acknowledge=True))
            print("published {}: {}".format(pub.id, payload))
        else:
            session.publish(topic, payload)


class SellingPublisher:
    """Publisher that sells the data on the XBR market."""
    def __init__(self, name):
        self._seller = None
        self._name = name
        self._topic = "{}.{}".format(WAMP_TOPIC_PREFIX, self._name)
        self._api_id = UUID('627f1b5c-58c2-43b1-8422-a34f7d3f5a04').bytes

    async def on_join(self, session):
        market_maker_adr = binascii.a2b_hex(session.config.extra['market_maker_adr'][2:])
        seller_privkey = binascii.a2b_hex(session.config.extra['seller_privkey'][2:])

        seller = SimpleSeller(market_maker_adr, seller_privkey)
        price = 35 * 10 ** 18
        interval = 300

        seller.add(self._api_id, self._topic, price, interval, None)
        balance = await seller.start(session)
        balance = int(balance / 10 ** 18)
        print("Remaining balance: {} XBR".format(balance))

        self._seller = seller

    async def publish(self, session, topic, payload):
        key_id, enc_ser, ciphertext = await self._seller.wrap(self._api_id, self._topic, payload)
        if DEBUG_ACK_SEND:
            pub = await session.publish(topic, key_id, enc_ser, ciphertext, options=PublishOptions(acknowledge=True))
            print("published {}: {}".format(pub.id, payload))
        else:
            session.publish(topic, key_id, enc_ser, ciphertext)

        if DEBUG_ENABLED:
            debug_topic = 'debug.' + topic
            session.publish(debug_topic, payload)


class VehicleFleetSimulation:
    """WAMP session handler for the vehicle fleet simulation.

    This is the base class for all concrete implementations of simulations.
    """
    def __init__(self, wamp_component, publisher, sumo_cfg, name):
        self._wamp = wamp_component
        self._publisher = publisher
        self._sumo_cfg = sumo_cfg
        self._name = name
        self._session = None
        self._driving_vehicles = []
        self._gui_enabled = False

        # associate ourselves with WAMP session lifecycle
        self._wamp.on('join', self.wamp_session_joined)
        self._wamp.on('leave', self.wamp_session_left)

        loop = asyncio.get_event_loop()
        loop.create_task(self._simu_task(self.get_simu_time_step_length()))

    async def wamp_session_joined(self, session, details):
        print("session joined")
        await self._publisher.on_join(session)
        self._session = session

    def wamp_session_left(self, session, reason):
        print("session left. reason: {}".format(reason))
        self._session = None

    async def try_publish(self, topic, data):
        """Publish data on a topic if connected to a WAMP router, otherwise just do nothing."""
        if self._session is not None:
            await self._publisher.publish(self._session, topic, data)

    async def simu_step_callback(self, subscription_results, context_subscription_results):
        """This function will be called on each simulated step.

        Overwrite this in your derived class with the wanted behaviour."""
        pass

    def _build_vehicle_topic(self, vehicle_id, suffix):
        """Return a WAMP topic to publish on."""
        hash = sha256(self._name.encode())
        hash.update(vehicle_id.encode())
        hashed_id = hash.hexdigest()
        return "{}.{}.{}.{}".format(WAMP_TOPIC_PREFIX, self._name, hashed_id, suffix)

    def _run_traci(self):
        """Start the simulation run."""
        command = 'sumo'
        if self._gui_enabled:
            command = command + '-gui'
        traci.start([command, '-c', self._sumo_cfg, '--duration-log.disable', '--no-step-log'])
        traci.simulation.subscribe([TC.VAR_ARRIVED_VEHICLES_IDS, TC.VAR_DEPARTED_VEHICLES_IDS])

    def _stop_traci(self):
        """Stop the simulation run."""
        traci.close()
        self._driving_vehicles = []

    async def _simu_task(self, simu_step):
        """Coroutine to run the simulation."""

        # TODO: generalize to enable subclasses to also define their stuff if needed
        def subscribe_departed(vehicle_id):
            """
            subscribes departed SUMO vehicle to traci
            """
            traci.vehicle.subscribeContext(
                "%s" % vehicle_id,
                TC.CMD_GET_VEHICLE_VARIABLE,
                10,
                (TC.VAR_ANGLE, TC.VAR_SLOPE, TC.VAR_POSITION, TC.VAR_SPEED)
            )

            traci.vehicle.subscribeContext(
                "%s" % vehicle_id,
                TC.CMD_GET_POI_VARIABLE,
                10,
                (TC.VAR_POSITION, TC.VAR_TYPE)
            )

            traci.vehicle.subscribe(
                "%s" % vehicle_id,
                (TC.VAR_POSITION, TC.VAR_SPEED, TC.VAR_ANGLE)
            )

        self._run_traci()

        while True:
            try:
                start = time.perf_counter()
                traci.simulationStep()
                sub_results = traci.simulation.getSubscriptionResults()
                departed = sub_results[TC.VAR_DEPARTED_VEHICLES_IDS]
                arrived = sub_results[TC.VAR_ARRIVED_VEHICLES_IDS]

                for vehicle_id in departed:
                    self._driving_vehicles.append(vehicle_id)
                    subscribe_departed(vehicle_id)

                for vehicle_id in arrived:
                    self._driving_vehicles.remove(vehicle_id)

                if not self._driving_vehicles:
                    self._stop_traci()
                    self._run_traci()

                vehicle_results = {}
                context_results = {}
                for vehicle_id in self._driving_vehicles:
                    res = traci.vehicle.getSubscriptionResults(vehicle_id)
                    if res is not None:
                        vehicle_results[vehicle_id] = res
                    res = traci.vehicle.getContextSubscriptionResults(vehicle_id)
                    if res is not None:
                        context_results[vehicle_id] = res

                await self.simu_step_callback(vehicle_results, context_results)

                end = time.perf_counter()
                delay = simu_step - (end - start)
                if delay < 0:
                    delay = 0
                await asyncio.sleep(delay)
            except traci.exceptions.FatalTraCIError:
                self._stop_traci()
                self._run_traci()

    def get_simu_time_step_length(self):
        """Get the simulation step length as defined in the SUMO config."""
        tree = ET.parse(self._sumo_cfg)
        step_length_element = tree.find('time/step-length')
        return float(step_length_element.attrib['value'])


class PositionProvidingFleetSimulation(VehicleFleetSimulation):
    """Fleet simulation to provide GPS data of each vehicle on WAMP.

    This is a simple example on how to write a concrete implementation of a fleet simulation.
    """
    def __init__(self, wamp_component, publisher, sumo_cfg, name):
        super().__init__(wamp_component, publisher, sumo_cfg, name)

    async def simu_step_callback(self, subscription_results, context_subscription_results):
        for vehicle_id, res in subscription_results.items():
            x, y = res[TC.VAR_POSITION]
            lng, lat = traci.simulation.convertGeo(x, y, fromGeo=False)
            now = time.time()

            topic = self._build_vehicle_topic(vehicle_id, 'position')
            data = {'lat': lat, 'lng': lng, 'ts': now}
            await self.try_publish(topic, data)


class PoiProvidingFleetSimulation(VehicleFleetSimulation):
    """Fleet simulation where each vehicle provides information about found POIs.
    """
    async def simu_step_callback(self, subscription_results, context_subscription_results):
        for vehicle_id, ctx in context_subscription_results.items():
            for key, val in ctx.items():
                try:
                    poi_type = val[TC.VAR_TYPE]
                    x, y = val[TC.VAR_POSITION]
                except (TypeError, KeyError):
                    # not the dict we are looking for
                    continue

                lng, lat = traci.simulation.convertGeo(x, y, fromGeo=False)
                now = time.time()

                topic = self._build_vehicle_topic(vehicle_id, 'poi')
                data = {'lat': lat, 'lng': lng, 'ts': now, 'type': poi_type}
                await self.try_publish(topic, data)


class ParkingPositionFleetSimulation(VehicleFleetSimulation):
    """Fleet simulation where each car provides data about observed parking spots.
    """
    def __init__(self, wamp_component, publisher, sumo_cfg, name):
        super().__init__(wamp_component, publisher, sumo_cfg, name)
        # We save the last found spot of each vehicle because in driving past we get multiple
        # context_subscription_results on subsequent simulation steps.
        #
        # This will not work 100% when there are parking spots very close to each other.
        # TODO: implement a better solution if that becomes a problem. {simu_step: (vehicle_id, poi_id)}?
        self._last_spots = {}  # key: vehicle, value: ID of last found parking spot

    async def simu_step_callback(self, subscription_results, context_subscription_results):
        for vehicle_id, res in subscription_results.items():
            # TODO: maybe not send the GPS position for every single simulation step
            x, y = res[TC.VAR_POSITION]
            lng, lat = traci.simulation.convertGeo(x, y, fromGeo=False)
            now = time.time()

            topic = self._build_vehicle_topic(vehicle_id, 'position')
            data = {'lat': lat, 'lng': lng, 'ts': now}
            await self.try_publish(topic, data)

        for vehicle_id, ctx in context_subscription_results.items():
            for key, val in ctx.items():
                try:
                    poi_type = val[TC.VAR_TYPE]
                except (TypeError, KeyError):
                    # not the dict we are looking for
                    continue
                if poi_type == 'parking':
                    if self.parking_spot_is_new(vehicle_id, key):
                        x, y = val[TC.VAR_POSITION]
                        lng, lat = traci.simulation.convertGeo(x, y, fromGeo=False)
                        now = time.time()

                        topic = self._build_vehicle_topic(vehicle_id, 'parking')
                        data = {'lat': lat, 'lng': lng, 'ts': now}
                        await self.try_publish(topic, data)

    def parking_spot_is_new(self, vehicle_id, poi_id):
        """Check if a vehicle found a new spot and save the information needed for future checks."""
        last = self._last_spots.get(vehicle_id)
        self._last_spots[vehicle_id] = poi_id
        if last is not None and last == poi_id:
            return False
        else:
            return True


class VehicleFleetFactory:
    TYPES = {
        'gps': PositionProvidingFleetSimulation,
        'parking': ParkingPositionFleetSimulation,
        'poi': PoiProvidingFleetSimulation,
    }

    def create_simulation(self, sim_type):
        klass = VehicleFleetFactory.TYPES.get(sim_type)
        if klass is None:
            print("Simulation type {} was specified, which is invalid. Possible values are: {}".format(
                sim_type,
                ", ".join(VehicleFleetFactory.TYPES.keys())
                )
            )
            exit(1)
        return klass


def parse_arguments():
    """Parse the command line arguments."""
    parser = argparse.ArgumentParser(description='Vehicle Fleet Simulation')
    parser.add_argument('-u', '--url', default=os.getenv('FLEET_SIM_URL', DEFAULT_URL), help='WAMP router URL')
    parser.add_argument('-r', '--realm', default=os.getenv('FLEET_SIM_REALM', DEFAULT_REALM), help='Realm to join on the WAMP router')
    parser.add_argument('-o', '--role', default=os.getenv('FLEET_SIM_ROLE', DEFAULT_ROLE), help='Desired role in the WAMP realm')
    parser.add_argument('-i', '--id', default=os.getenv('FLEET_SIM_ID'), help='The user ID used for authentication. Not needed for anonymous authentication.')
    parser.add_argument('-t', '--ticket', default=os.getenv('FLEET_SIM_TICKET'), help='The ticket for ticket authentication. If this is specified an ID has also to be provided.')
    parser.add_argument('-n', '--name', default=os.getenv('FLEET_SIM_NAME', DEFAULT_SIMU_NAME), help='Name of the fleet to differentiate between different simulations')
    parser.add_argument('--type', default=os.getenv('FLEET_SIM_TYPE', 'gps'), help='The type of the fleet simulation')
    parser.add_argument('-k', '--privkey', default=os.getenv('FLEET_SIM_PRIVKEY'), help='Private key used for selling the data')
    parser.add_argument('sumo_cfg', metavar='SUMO_CFG', help='The SUMO configuration to be used')

    return parser.parse_args()


def build_authentication(args):
    """Build the authentication dictionary a Component expects."""
    extra = {'service_name': 'Vehicle Fleet Simulation for {}'.format(args.name)}

    if args.ticket is not None:
        # Ticket authentication
        if args.id is None:
            print("Ticket authentication was specified, but no ID was provided!")
            exit(1)

        auth = {
            'ticket': {
                'authid': args.id,
                'ticket': args.ticket,
                'authrole': args.role,
                'authextra': extra,
            }
        }
    # TODO: Extend for other authentication methods. Should multiple methods be possible?
    else:
        # falling back to anonymous
        auth = {
            'anonymous': {
                'authrole': args.role,
                'authextra': extra,
            }
        }

    return auth


def main(options):
    """Main function."""
    auth = build_authentication(options)
    comp = Component(
                transports=[{
                    'url': args.url,
                    'max_retries': -1,
                    'max_retry_delay': 30,
                }],
                realm=args.realm,
                authentication=auth,
                extra={
                    'market_maker_adr': os.environ.get(
                        'XBR_MARKET_MAKER_ADR',
                        '0x3e5e9111ae8eb78fe1cc3bb8915d5d461f3ef9a9'
                    ),
                    'seller_privkey': options.privkey,
                }
            )

    if options.privkey is None:
        pub = WampPublisher()
    else:
        pub = SellingPublisher(options.name)

    factory = VehicleFleetFactory()
    sim_type = factory.create_simulation(options.type)
    _ = sim_type(comp, pub, options.sumo_cfg, options.name)

    run([comp])


if __name__ == '__main__':
    print("Starting")
    try:
        args = parse_arguments()
        main(args)
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("Unexpected exception:", e)
    finally:
        print("Exiting")

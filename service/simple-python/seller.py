#!/usr/bin/env python3
"""Simple Seller example.
"""

from autobahn.twisted.xbr import SimpleSeller
from autobahn.twisted.util import sleep
from autobahn.twisted.component import Component, run
from autobahn.wamp.types import PublishOptions
import binascii
import os
from time import sleep
from uuid import UUID
import txaio
txaio.use_twisted()


DEFAULT_AUTHID = 'team1'
DEFAULT_TICKET = 'apple pear orange fig'

comp = Component(
    transports=os.environ.get(
        'XBR_INSTANCE', 'wss://continental2.crossbario.com/ws'),
    realm=os.environ.get('XBR_REALM', 'realm1'),
    authentication={
        'ticket': {
            'authid': os.environ.get('XBR_AUTHID', DEFAULT_AUTHID),
            'ticket': os.environ.get('XBR_TICKET', DEFAULT_TICKET),
        },
    },
    extra={
        'market_maker_adr': os.environ.get('XBR_MARKET_MAKER_ADR', '0x3e5e9111ae8eb78fe1cc3bb8915d5d461f3ef9a9'),
        'seller_privkey': os.environ.get('XBR_SELLER_PRIVKEY', '0x496fbc218ffb1afe839b93cce01819433df1b72034a94ec46d83592c7342d632'),
    }
)

running = False


@comp.on_join
async def joined(session, details):
    print('Seller session joined', details)
    global running
    running = True

    market_maker_adr = binascii.a2b_hex(
        session.config.extra['market_maker_adr'][2:])
    print('Using market maker adr:', session.config.extra['market_maker_adr'])

    seller_privkey = binascii.a2b_hex(
        session.config.extra['seller_privkey'][2:])

    api_id = UUID('627f1b5c-58c2-43b1-8422-a34f7d3f5a04').bytes
    topic = 'com.conti.hackathon.team1.sell'
    counter = 1

    seller = SimpleSeller(market_maker_adr, seller_privkey)
    price = 35 * 10 ** 18
    interval = 10
    seller.add(api_id, topic, price, interval, None)

    balance = await seller.start(session)
    balance = int(balance / 10 ** 18)
    print("Remaining balance: {} XBR".format(balance))

    while running:
        payload = {'data': 'py-seller', 'counter': counter}
        key_id, enc_ser, ciphertext = await seller.wrap(api_id,
                                                        topic,
                                                        payload)
        pub = await session.publish(topic, key_id, enc_ser, ciphertext,
                                    options=PublishOptions(acknowledge=True))

        print('Published event {}: {}'.format(pub.id, payload))

        counter += 1
        await sleep(10)


@comp.on_leave
def left(session, details):
    print('Seller session left', details)
    global running
    running = False


if __name__ == '__main__':
    run([comp])

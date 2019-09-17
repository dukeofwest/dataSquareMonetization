#!/usr/bin/env python3
"""Simple Buyer example.
"""

from autobahn.twisted.xbr import SimpleBuyer
from autobahn.twisted.xbr import SimpleSeller
from autobahn.twisted.component import Component, run
from autobahn.wamp.types import SubscribeOptions
from autobahn.wamp.types import PublishOptions
import binascii
import os
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
        'buyer_privkey': os.environ.get('XBR_BUYER_PRIVKEY', '0x16A60CED74B0D0523567B2261CF3E1C41048036D291D7132BF353E10B74F817A'),
    }
)


@comp.on_join
async def joined(session, details):
    print('Buyer session joined', details)

    market_maker_adr = binascii.a2b_hex(
        session.config.extra['market_maker_adr'][2:])
    print('Using market maker adr:', session.config.extra['market_maker_adr'])

    buyer_privkey = binascii.a2b_hex(session.config.extra['buyer_privkey'][2:])

    max_price = 100 * 10 ** 18
    buyer = SimpleBuyer(market_maker_adr, buyer_privkey, max_price)
    balance = await buyer.start(session, details.authid)
    balance = int(balance / 10 ** 18)
    print("Remaining balance: {} XBR".format(balance))

    # seller
    seller_privkey = binascii.a2b_hex(
        session.config.extra['seller_privkey'][2:])

    api_id = UUID('627f1b5c-58c2-43b1-8422-a34f7d3f5a04').bytes
    topic_seller = 'com.conti.hackathon.team1.sell'
    topic_buyer = "com.conti.hackathon.team1"
    counter = 1

    seller = SimpleSeller(market_maker_adr, seller_privkey)
    price = 35 * 10 ** 18
    interval = 10
    seller.add(api_id, topic_seller, price, interval, None)

    balance = await seller.start(session)
    balance = int(balance / 10 ** 18)
    print("Remaining balance: {} XBR".format(balance))

    async def on_event(key_id, enc_ser, ciphertext, details=None):
        try:
            payload = await buyer.unwrap(key_id, enc_ser, ciphertext)
            print(payload)
            key_id, enc_ser, ciphertext = await seller.wrap(api_id,
                                                            topic_seller,
                                                            payload)
            pub = await session.publish(topic_seller, key_id, enc_ser, ciphertext,
                                        options=PublishOptions(acknowledge=True))

            print('Published event {}: {}'.format(pub.id, payload))

        except Exception as e:
            print(e)
            session.leave()
        else:
            print('Received event {}:'.format(details.publication), payload)

    await session.subscribe(on_event, topic_buyer, options=SubscribeOptions(details=True, match="prefix"))


if __name__ == '__main__':
    run([comp])

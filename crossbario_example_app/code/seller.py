import binascii
import os
from uuid import UUID

from autobahn.twisted.component import Component, run
from autobahn.wamp.types import PublishOptions
from autobahn.twisted.xbr import SimpleSeller

extra = {
    'market_maker_adr': os.environ.get('XBR_MARKET_MAKER_ADR', '0x3e5e9111ae8eb78fe1cc3bb8915d5d461f3ef9a9'),
    'seller_privkey': os.environ.get('XBR_SELLER_PRIVKEY',
                                     '0xadd53f9a7e588d003326d1cbf9e4a43c061aadd9bc938c843a79e7b4fd2ad743'),
}
seller_component = Component(
    transports=os.environ.get('XBR_INSTANCE', u'ws://localhost:8080/ws'),
    realm=os.environ.get('XBR_REALM', u'realm1'),
    extra=extra
)


@seller_component.on_join
async def joined(session, details):
    print('Seller session joined', details)

    market_maker_adr = binascii.a2b_hex(session.config.extra['market_maker_adr'][2:])
    print('Using market maker adr:', session.config.extra['market_maker_adr'])
    seller_privkey = binascii.a2b_hex(session.config.extra['seller_privkey'][2:])

    api_id = UUID('627f1b5c-58c2-43b1-8422-a34f7d3f5a04').bytes
    topic = 'io.crossbar.example'

    seller = SimpleSeller(market_maker_adr, seller_privkey)
    # 1 XBR
    price = 1 * 10 ** 18
    interval = 12
    seller.add(api_id, topic, price, interval, None)

    balance = await seller.start(session)
    balance = int(balance / 10 ** 18)
    print("Remaining balance: {} XBR".format(balance))

    async def on_odometer_data(count):
        print("event received: {}".format(count))
        payload = {'data': 'py-seller', 'counter': count}
        key_id, enc_ser, ciphertext = await seller.wrap(api_id, topic, payload)
        pub = await session.publish(topic, key_id, enc_ser, ciphertext,
                                    options=PublishOptions(acknowledge=True))

        print('Published event {}: {}'.format(pub.id, payload))

    try:
        await session.subscribe(on_odometer_data, "xbr.myapp.odometer")
        print("subscribed to topic '{}'".format("xbr.myapp.odometer"))
    except Exception as e:
        print("could not subscribe to topic: {}".format(e))


if __name__ == '__main__':
    run([seller_component])

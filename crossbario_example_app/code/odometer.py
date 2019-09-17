###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

import datetime
import os
import random

from autobahn.twisted.component import Component, run
import txaio


odometer_component = Component(
    transports=os.environ.get('XBR_INSTANCE', u'ws://localhost:8080/ws'),
    realm=os.environ.get('XBR_REALM', u'realm1')
)


@odometer_component.on_join
async def joined(session, _details):
    print("session joined...")
    counter = 20000
    while session.is_attached():
        date = datetime.datetime.now()
        print('Odometer Simulator publishing xbr.myapp.odometer', counter, date)
        session.publish(u'xbr.myapp.odometer', f'{counter} {date}')
        counter += random.randint(1, 10)
        await txaio.sleep(1)


if __name__ == '__main__':
    run([odometer_component])

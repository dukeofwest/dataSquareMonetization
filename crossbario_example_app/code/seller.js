let autobahn = require('autobahn');
let xbr = require('autobahn-xbr');

console.log('Running on Autobahn ' + autobahn.version);
console.log('Running Autobahn-XBR ' + xbr.version);

const url = process.env.XBR_INSTANCE || "ws://localhost:8080/ws";
const realm = process.env.XBR_REALM || "realm1";
const seller_privkey = process.env.XBR_SELLER_PRIVKEY;
const marketmaker_addr = process.env.XBR_MARKET_MAKER_ADR;


// WAMP connection
let connection = new autobahn.Connection({
  realm: realm,
  transports: [
    {
      url: url,
      type: 'websocket',
      serializers: [ new autobahn.serializer.CBORSerializer() ],
    }
  ]
});


// callback fired upon new WAMP session
connection.onopen = function (session, details) {

  console.log("WAMP session connected:", details);


  // the XBR token has 18 decimals
  const decimals = new xbr.BN('1000000000000000000');

  // price in XBR per key
  const price = new xbr.BN(35).mul(decimals);

  // key rotation interval in seconds
  const key_rotation_interval = 10;

  // API ID of the interface of the offered service
  const api_id = xbr.uuid('bd65e220-aef7-43c0-a801-f8d95fa71f39');

  // instantiate a simple seller
  let seller = new xbr.SimpleSeller(marketmaker_addr, seller_privkey);
  let counter = 1;

  seller.add(api_id, 'io.crossbar.example', price, key_rotation_interval);


  let do_publish = function(counter) {
    const payload = {"data": "js-node-seller", "counter": counter};

    // encrypt the XBR payload, potentially automatically rotating & offering a new data encryption key
    let [key_id, enc_ser, ciphertext] = seller.wrap(api_id, 'io.crossbar.example', payload);

    const options = {acknowledge: true};

    session.publish("io.crossbar.example",
        [key_id, enc_ser, ciphertext],
        {},
        options).then(
        function (pub) {
          console.log("Published event " + pub.id);
        },
        function (err) {
          console.log("Failed to publish event", err);
        }
    );

  };
  function on_cardata (args) {
    data = args[0];
    do_publish(data);
    console.log("on_counter() event received with counter " + data);
  }

  session.subscribe('xbr.myapp.odometer', on_cardata).then(
      function (sub) {
        console.log(' xbr.myapp.odometer subscribed to topic');

      },
      function (err) {
        console.log('xbr.myapp.cardata failed to subscribe to topic', err);
      }
  );
  // start selling
  seller.start(session).then(
      // success: we've got an active paying channel with remaining balance ..
      function (balance) {
        console.log("Seller has started, remaining balance in active paying channel is " + balance.div(decimals) + " XBR");
        do_publish();
      },
      // we don't have an active paying channel => bail out
      function (error) {
        console.log("Failed to start seller:", error);
        process.exit(1);
      }
  );
};


// open WAMP session
connection.open();

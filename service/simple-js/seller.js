var autobahn = require('autobahn');
var xbr = require('autobahn-xbr');
var web3 = require('web3');
var BN = web3.utils.BN;
var uuid = require('uuid-buffer');

console.log('Running on Autobahn ' + autobahn.version);
//Private key of your seller delegate
const SELLER_PRIVATEKEY = "0xA546A4953D3953EB3A6BE8E64364936F71D1C51913A3A02180D15CEA352B2A0D";
//Market maker address
const MARKET_MAKER_ADDR = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9";
//TEAM_ID
const TEAM_ID = "team1";
//TICKET
const TICKET = "apple pear orange fig";
//TOPIC TO SUBSCRIBE TO
const TOPIC = "com.conti.hackathon.team1.topic1";

//Connect to Crossbarfx node
var connection = new autobahn.Connection({
    realm: "realm1",
    authmethods: ["ticket"],
    authid: TEAM_ID,
    onchallenge: onchallenge,
    transports: [
      {
        url: "wss://continental2.crossbario.com/ws",
        type: "websocket",
        serializers: [new autobahn.serializer.CBORSerializer()]
      }
    ]
  });
  
  //Only for authentication on crossbar
  function onchallenge(session, method, extra) {
    if (method === "ticket") {
      return TICKET;
    } else {
      throw "don't know how to authenticate using '" + method + "'";
    }
  };

// callback fired upon new WAMP session
connection.onopen = function (session, details) {

    console.log("WAMP session connected:", details);

    // the XBR token has 18 decimals
    const decimals = new BN('1000000000000000000');

    // price in XBR per key
    const price = new BN(35).mul(decimals);

    // key rotation interval in seconds
    const key_rotation_interval = 10;

    // API ID of the interface of the offered service
    const apiID = uuid.toBuffer('bd65e220-aef7-43c0-a801-f8d95fa71f39');

    // instantiate a simple seller
    var seller = new xbr.SimpleSeller(MARKET_MAKER_ADDR, SELLER_PRIVATEKEY);
    var counter = 1;

    seller.add(apiID, TOPIC, price, key_rotation_interval);

    var do_publish = function() {
        const payload = {"data": "js-seller", "counter": counter};

        // encrypt the XBR payload, potentially automatically rotating & offering a new data encryption key
        let [key_id, enc_ser, ciphertext] = seller.wrap(apiID, TOPIC, payload);

        const options = {acknowledge: true};

        session.publish(TOPIC,
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

        counter += 1;
        setTimeout(do_publish, 1000);
    };

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

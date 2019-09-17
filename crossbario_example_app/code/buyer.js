var autobahn = require('autobahn');
var xbr = require('autobahn-xbr');

console.log('Running on Autobahn ' + autobahn.version);
console.log('Running Autobahn-XBR ' + xbr.version);
const url = process.env.XBR_INSTANCE || "ws://localhost:8080/ws";
const realm = process.env.XBR_REALM || "realm1";
const buyer_privkey = process.env.XBR_BUYER_PRIVKEY;
const marketmaker_addr = process.env.XBR_MARKET_MAKER_ADR;


// WAMP connection
var connection = new autobahn.Connection({
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

    // maximum price we are willing to pay per (single) key: 100 XBR
    const max_price = new xbr.BN('100').mul(decimals);

    // instantiate a simple buyer
    var buyer = new xbr.SimpleBuyer(marketmaker_addr, buyer_privkey, max_price);

    // start buying ..
    buyer.start(session).then(
        // success: we've got an active payment channel with remaining balance ..
        function (balance) {
            console.log("Buyer has started, remaining balance in active payment channel is " + balance.div(decimals) + " XBR");

            session.subscribe("io.crossbar.example", function (args, kwargs, details) {
                let [key_id, enc_ser, ciphertext] = args;

                // decrypt the XBR payload, potentially automatically buying a new data encryption key
                buyer.unwrap(key_id, enc_ser, ciphertext).then(
                    function (payload) {
                        console.log("Received event " + details.publication, payload)
                        session.publish('xbr.myapp.cardata', [payload['counter']]);
                    },
                    function (failure) {
                        console.log(failure);
                        process.exit(1);
                    }
                )
            });

        },
        // we don't have an active payment channel => bail out
        function (error) {
            console.log("Failed to start buyer:", error);
            process.exit(1);
        }
    );
};

// open WAMP session
connection.open();

var autobahn = require("autobahn");
var xbr = require("autobahn-xbr");
var web3 = require("web3");
var BN = web3.utils.BN;

console.log("Running on Autobahn " + autobahn.version);
//Private key of your buyer delegate
const BUYER_PRIVATEKEY = "0x16A60CED74B0D0523567B2261CF3E1C41048036D291D7132BF353E10B74F817A";
//Market maker address
const MARKET_MAKER_ADDR = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9";
//TEAM_ID
const TEAM_ID = "team1";
//TICKET
const TICKET = "apple pear orange fig";
//TOPIC TO SUBSCRIBE TO
const TOPIC = "com.conti.hackathon.team1.topic3";

//Connect to Crossbarfx node
var connection = new autobahn.Connection({
    realm: "realm1",
    authmethods: ["ticket"],
    authid: TEAM_ID,
    onchallenge: onchallenge,
    transports: [{
        url: "wss://continental2.crossbario.com/ws",
        type: "websocket",
        serializers: [new autobahn.serializer.CBORSerializer()]
    }]
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
connection.onopen = function(session, details) {
    console.log("WAMP session connected:", details);

    // the XBR token has 18 decimals
    const decimals = new BN("1000000000000000000");

    // maximum price we are willing to pay per (single) key: 100 XBR
    const max_price = new BN("100").mul(decimals);

    // instantiate a simple buyer
    var buyer = new xbr.SimpleBuyer(
        MARKET_MAKER_ADDR,
        BUYER_PRIVATEKEY,
        max_price
    );

    // start buying ..
    buyer.start(session).then(
        // success: we've got an active payment channel with remaining balance ..
        function(balance) {
            console.log(
                "Buyer has started, remaining balance in active payment channel is " +
                balance.div(decimals) +
                " XBR"
            );

            session.subscribe(TOPIC, function(args, kwargs, details) {
                let [key_id, enc_ser, ciphertext] = args;

                // decrypt the XBR payload, potentially automatically buying a new data encryption key
                buyer.unwrap(key_id, enc_ser, ciphertext).then(
                    function(payload) {
                        console.log("Received event " + details.publication, payload);
                    },
                    function(failure) {
                        console.log(failure);
                        process.exit(1);
                    }
                );
            }, { match: "prefix" });
        },
        // we don't have an active payment channel => bail out
        function(error) {
            console.log("Failed to start buyer:", error);
            process.exit(1);
        }
    );
};

// open WAMP session
connection.open();
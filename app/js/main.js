const xbr = autobahnXbr;
console.log('Running Autobahn ' + autobahn.version);
console.log('Running Autobahn-XBR ' + xbr.version);

//Private key of your persona
const PERSONA_PRIVATEKEY = "0x67C8B5ADD595C63028AC49C9BAFF347C1E57E9625782D1010B938FF814816B6C";
//Market maker address
const MARKET_MAKER_ADDR = "0x3E5e9111Ae8eB78Fe1CC3bb8915d5D461F3Ef9A9";
//TEAM_ID
const TEAM_ID = "team1";
//TICKET
const TICKET = "apple pear orange fig";
//TOPIC TO SUBSCRIBE TO
const TOPIC = "com.conti.hackathon.team1.sell";
//OPTIN RPC TOPIC
const OPTIN_RPC = "com.conti.hackathon.team1.optin";
const decimals = new xbr.BN("1000000000000000000");
//Connect to Crossbarfx node
var connection = new autobahn.Connection({
    realm: "realm1",
    authmethods: ["ticket"],
    authid: TEAM_ID,
    onchallenge: onchallenge,
    transports: [{
        url: 'wss://continental2.crossbario.com/ws',
        type: 'websocket',
        serializers: [new autobahn.serializer.MsgpackSerializer()]
    }]
});

function accountBalance() {
    document.getElementById("accBalance").innerHTML = "Balance: " + autobahn.version;
}
//Calls the map

mapboxgl.accessToken = 'pk.eyJ1IjoiZHVrZW9md2VzdCIsImEiOiJjazBubW01cG0wMWJ6M2Jxcmo5ZmloNWhuIn0.Dzm68frXiowBKT9u21DlyQ';
var map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [-122.486052, 37.830348],
    zoom: 15
});

// map.on('load', function() {

//     map.addLayer({
//         "id": "route",
//         "type": "line",
//         "source": {
//             "type": "geojson",
//             "data": {
//                 "type": "Feature",
//                 "properties": {},
//                 "geometry": {
//                     "type": "LineString",
//                     "coordinates": [
//                         [-122.48369693756104, 37.83381888486939],
//                         [-122.48348236083984, 37.83317489144141],
//                         [-122.48339653015138, 37.83270036637107],
//                         [-122.48356819152832, 37.832056363179625],
//                         [-122.48404026031496, 37.83114119107971],
//                         [-122.48404026031496, 37.83049717427869],
//                         [-122.48348236083984, 37.829920943955045],
//                         [-122.48356819152832, 37.82954808664175],
//                         [-122.48507022857666, 37.82944639795659],
//                         [-122.48610019683838, 37.82880236636284],
//                         [-122.48695850372314, 37.82931081282506],
//                         [-122.48700141906738, 37.83080223556934],
//                         [-122.48751640319824, 37.83168351665737],
//                         [-122.48803138732912, 37.832158048267786],
//                         [-122.48888969421387, 37.83297152392784],
//                         [-122.48987674713133, 37.83263257682617],
//                         [-122.49043464660643, 37.832937629287755],
//                         [-122.49125003814696, 37.832429207817725],
//                         [-122.49163627624512, 37.832564787218985],
//                         [-122.49223709106445, 37.83337825839438],
//                         [-122.49378204345702, 37.83368330777276]
//                     ]
//                 }
//             }
//         },
//         "layout": {
//             "line-join": "round",
//             "line-cap": "round"
//         },
//         "paint": {
//             "line-color": "#888",
//             "line-width": 8
//         }
//     });
// });


//Only for authentication on crossbar
function onchallenge(session, method, extra) {
    if (method === "ticket") {
        return TICKET;
    } else {
        throw "don't know how to authenticate using '" + method + "'";
    }
}

connection.onopen = function(session) {
    console.log("Connected To Crossbarfx");
    const listGroup = document.getElementById("list-group");
    const buyButton = document.getElementById("buy_data_button");
    const optInButton = document.getElementById("opt_in_button");
    accountBalance();
    // the XBR token has 18 decimals
    const decimals = new xbr.BN("1000000000000000000");

    // maximum price we are willing to pay per (single) key: 100 XBR
    const max_price = new xbr.BN("100").mul(decimals);

    // instantiate a simple buyer
    var buyer = new xbr.SimpleBuyer(
        MARKET_MAKER_ADDR,
        PERSONA_PRIVATEKEY,
        max_price
    );

    // start buyer
    buyer.start(session).then(
        // success: we've got an active payment channel with remaining balance ..
        function(balance) {
            console.log('Delegate wallet balance: ' + balance.div(decimals).toString() + ' XBR');
            setInterval(function() {
                buyer.balance().then(function(success) {
                    const amount = new xbr.BN(success.amount).div(decimals);
                    document.getElementById("accBalance").innerHTML = "Balance: " + amount.toString();
                    console.log(success);

                }, function(error) {
                    console.log("Failed to start buyer:", error);
                })
            }, 500);
        },
        // we don't have an active payment channel => bail out
        function(error) {
            console.log("Failed to start buyer:", error);
        }
    );

    //Handler for buy button
    buyButton.addEventListener("click", e => {
        e.preventDefault();
        session.subscribe(TOPIC, function(args, kwargs, details) {
            let [key_id, enc_ser, ciphertext] = args;
            // decrypt the XBR payload, potentially automatically buying a new data encryption key
            buyer.unwrap(key_id, enc_ser, ciphertext).then(
                function(payload) {
                    console.log("Received event " + details.publication, payload);
                    //Callback triggered on publish event
                    if (payload) {
                        const lat = payload.lat;
                        const lon = payload.lng;
                        const node = document.createElement("li");
                        const textNode = document.createTextNode(
                            "Lat: " + lat + " Lon:" + lon
                        );
                        node.className = "list-group-item";
                        node.appendChild(textNode);
                        listGroup.appendChild(node);
                    }
                },
                function(failure) {
                    console.log(failure);
                    location.reload(true);
                }
            )
        }, { match: 'prefix' });
    });

    //Handler for opt-in
    optInButton.addEventListener("click", e => {
        e.preventDefault();
        //Implement rpc function on the backend
        session.call(OPTIN_RPC).then(
            success => {
                if (success) {
                    //If subscription is successfull register to topic
                    console.log("Opt-in successful");
                    buyButton.removeAttribute("disabled");
                    optInButton.setAttribute("disabled", true);
                }
            },
            error => {
                console.log(error);
            }
        );
    });
};

connection.open()
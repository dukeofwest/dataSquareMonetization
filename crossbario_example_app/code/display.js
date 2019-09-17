// Example WAMP client for AutobahnJS connecting to a Crossbar.io WAMP router.
// AutobahnJS, the WAMP client library to connect and talk to Crossbar.io:

// Car gif from https://gifer.com/en/Un8o
let isBrowser = false;
try {
    let autobahn = require('autobahn');
} catch (e) {
    // when running in browser, AutobahnJS will
    // be included without a module system
    isBrowser = true;
}
console.log("Running AutobahnJS " + autobahn.version);
let url = null;
let realm = null;

if (isBrowser) {
    url = 'wss://continental2.crossbario.com/ws';
    realm = 'realm1';
}
else {
  url = process.env.XBR_INSTANCE || "ws://localhost:8080/ws";
  realm = process.env.XBR_REALM || "realm1";
}
let connection = new autobahn.Connection({ url: url, realm: realm });
console.log("Running AutobahnJS " + url+ "  "+realm);

// .. and fire this code when we got a session
connection.onopen = function (session, details) {
    console.log("session open!", details);
    // Your code goes here: use WAMP via the session you got to
    // call, register, subscribe and publish ..
 setInterval(function () {
    session.call("xbr.myapp.get_distance",[]).then(
    function(res) {
    let array = res.split(" ");
    let distance = array[0]
    let percentage = ((distance)/200000)*100;
    percentage = percentage.toFixed(2);

    document.getElementById('progressbar').value = percentage;
    document.getElementById('id_distance').innerHTML = "Total distance travelled: "+distance+" Kms";
    document.getElementById('id_percentage').innerHTML = "Percentage:"+percentage+"%";    
    console.log('Distance is', distance);
    console.log('Percentage is', percentage);

    }, session.log);
     
   }, 1000);

};

// .. and fire this code when our session has gone
connection.onclose = function (reason, details) {
    console.log("session closed: " + reason, details);
};

// Don't forget to actually trigger the opening of the connection!
connection.open();

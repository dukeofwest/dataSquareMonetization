// Example WAMP client for AutobahnJS connecting to a Crossbar.io WAMP router.

// AutobahnJS, the WAMP client library to connect and talk to Crossbar.io:
let autobahn = require("autobahn");

console.log("Running AutobahnJS " + autobahn.version);

// We read the connection parameters from the command line in this example:
const url = process.env.XBR_INSTANCE || "ws://localhost:8080/ws";
const realm = process.env.XBR_REALM || "realm1";

// Make us a new connection ..
let connection = new autobahn.Connection({url: url, realm: realm});
let counter = 20000;
// .. and fire this code when we got a session
connection.onopen = function (session, details) {
  console.log("session open!", details);

  setInterval(function () {
    console.log("publishing to xbr.myapp.odometer");
    counter += Math.floor(Math.random() * 10);
    let date = new Date().toISOString();
    session.publish("xbr.myapp.odometer", [counter + " " + date]);
  }, 1000);
};

// .. and fire this code when our session has gone
connection.onclose = function (reason, details) {
  console.log("session closed: " + reason, details);
};

// Don"t forget to actually trigger the opening of the connection!
connection.open();

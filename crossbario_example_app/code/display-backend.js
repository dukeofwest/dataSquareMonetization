// Example WAMP client for AutobahnJS connecting to a Crossbar.io WAMP router.

// AutobahnJS, the WAMP client library to connect and talk to Crossbar.io:
let autobahn = require('autobahn');

console.log("Running AutobahnJS " + autobahn.version);

// We read the connection parameters from the command line in this example:
const url = process.env.XBR_INSTANCE || "ws://localhost:8080/ws";
const realm = process.env.XBR_REALM || "realm1";

// Make us a new connection ..
let connection = new autobahn.Connection({url: url, realm: realm});
// .. and fire this code when we got a session
connection.onopen = function (session, details) {
  console.log("session open!", details);
  let data = null;

  function get_distance(args) {
    return data;
  }

  session.register('xbr.myapp.get_distance', get_distance).then(
      function (reg) {
        console.log('procedure registered', reg.procedure);
      },
      function (err) {
        console.log('xbr.myapp.get_distance failed to register procedure', err);
      }
  );

  function on_cardata(args) {
    data = args[0];
    console.log("on_counter() event received with counter " + data);
  }

  session.subscribe('xbr.myapp.cardata', on_cardata).then(
      function (sub) {
        console.log('subscribed to topic', sub.topic);
      },
      function (err) {
        console.log('xbr.myapp.cardata failed to subscribe to topic', err);
      }
  );
};

// .. and fire this code when our session has gone
connection.onclose = function (reason, details) {
  console.log("session closed: " + reason, details);
};

// Don't forget to actually trigger the opening of the connection!
connection.open();

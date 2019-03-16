var socket = io.connect('http://' + document.domain + ':' + location.port);

socket.heartbeatTimeout = 20000;

socket.on('connect', function() {
    // we emit a connected message to let knwo the client that we are connected.
//    socket.emit('client_connected', {data: 'New client!'});
    console.log('connected');
});

//    var source = new EventSource('/sse-stream');
//    source.onmessage = function (event) {
//        console.log('get new event from stream', event);
//        document.getElementById('out').innerHTML = 'new data:' + event.data;
//    };

const fetchValue = id => document.getElementById( id ).value;

document.addEventListener("DOMContentLoaded", function(event) {

    // change base state level or value form
    var state_form = document.getElementById('state-form');
    state_form.addEventListener('submit', (e) => {
        color = fetchValue ( 'state-color' );
        value = fetchValue ( 'state-value' );
        console.log('sent state', {'color': color, 'value': value});
        socket.emit('state', {'color': color, 'value': value});
        e.preventDefault();
        state_form.reset();
    });

    // header elements 

    var alertList = document.getElementById('alert_list');
    alertList.addEventListener('click', function() {
        var cont = document.getElementById('alert_contain');
        if (cont.style.display == 'none' || !cont.style.display) {
            cont.style.display = 'block';
        } else {
            cont.style.display = 'none';
        }
    }, false);

    

});


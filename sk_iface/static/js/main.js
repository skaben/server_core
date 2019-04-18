  $(document).ready(function () {
    var accordions = bulmaAccordion.attach();
    var websocket = new WebSocket('ws://' + window.location.host + '/ws/');

    websocket.onopen = function open() {
      console.log('WebSockets connection created.');
    };

    var btn = document.getElementById('btn');
    btn.onclick = function() {
      console.log('pressed');
      websocket.send('testdata');
    }

    if (websocket.readyState == WebSocket.OPEN) {
      websocket.onopen();
    }

    // обработчик входящих сообщений
    websocket.onmessage = function(event) {
      if (typeof event.data === 'string') {
        var jsonObject = JSON.parse(event.data);
        var timestamp = jsonObject.time;
        var content = JSON.stringify(jsonObject.data);
        showMessage(timestamp, content);
      }
    };

    const msg_log = document.getElementById("message_log")
    let c = 0

    // show message in message log (with scroll to bottom)
    function showMessage(timestamp, content) {
      const isScrolledToBottom = msg_log.scrollHeight - msg_log.clientHeight <= msg_log.scrollTop + 1
      var messageElem = document.createElement('div');
      messageElem.classList.add('message_msg');
      messageElem.appendChild(document.createTextNode(timestamp + ' '));
      messageElem.appendChild(document.createTextNode(content));
      msg_log.appendChild(messageElem);
      if (isScrolledToBottom) {
        msg_log.scrollTop = msg_log.scrollHeight - msg_log.clientHeight
      }
    }


    $('a.touch').on('click', function(e) {
      e.preventDefault();
      var url = $(this).attr('href');
      $.get(url, function() {
        // success
      });
    });
  });

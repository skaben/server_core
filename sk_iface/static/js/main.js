  $(document).ready(function () {

    // using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // ACCORDION

    var accordions = bulmaAccordion.attach();

    // WEBSOCKETS

    var websocket = new WebSocket('ws://' + window.location.host + '/ws/');

    websocket.onopen = function open() {
      console.log('WebSockets connection created.');
    };

    if (websocket.readyState == WebSocket.OPEN) {
      websocket.onopen();
    }

    // обработчик входящих сообщений
    websocket.onmessage = function(event) {
      if (typeof event.data === 'string') {
        var jsonObject = JSON.parse(event.data);
        if (jsonObject.type === 'ws.log') {
          console.log('writing log...');
          console.log(jsonObject);
          var timestamp = jsonObject.time;
          var content = JSON.stringify(jsonObject.data);
          showMessage(timestamp, content);
        }
        if (jsonObject.type === 'ws.update') {
          console.log(jsonObject.content);
          var name = jsonObject.content.name;
          if (name === 'full') {
            // ok, that's simple and dirty hack
            window.location.reload(true);
          } else {
            var id = jsonObject.content.id;
            reloadDiv('#' + name + "-" + id);
          }
        }
      }
    };

    function reloadDiv(area_id) {
      $(area_id).load(' '+area_id,
                          function(){$(this).children().unwrap()})
    }

    const msg_log = document.getElementById("message_log")
    let c = 0

    // show message in message log (with scroll to bottom)
    function showMessage(timestamp, content) {
      const isScrolledToBottom = msg_log.scrollHeight - msg_log.clientHeight <= msg_log.scrollTop + 1
      var messageElem = document.createElement('div');
      messageElem.classList.add('message_msg');
      messageElem.appendChild(document.createTextNode(timestamp + '> '));
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

    $(document).on('click', '.details-toggle', function(e){
      e.preventDefault();
      $($(this).attr('href')).slideToggle(220);
    });

    $('.dev_li').dblclick(function(){
      console.log('double click');
    });

  });

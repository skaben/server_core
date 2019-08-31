import os
import sys
import json
import pytest

basedir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(basedir)

sys.path.append(parentdir)

from sk_mqtts.tests.mocks import server, mock_message

def test_server_mocks():
    publish = server.publish('test')
    assert publish == str('test')
    event = server.send_event('event')
    assert event == str('event')

def test_server_on_message_std():
    msg = mock_message()
    event = server.on_message('', '', msg)
    assert isinstance(event, dict)
    for key in ('dev_type','uid', 'command', 'payload', 'type'):
        assert event.get(key), f'<{key}> missing from event'
    assert event.get('type') == 'device.event', f'bad type for {event}'






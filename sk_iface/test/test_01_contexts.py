import pytest


from sk_iface.event_contexts import DeviceEventContext, ServerEventContext
from sk_iface.event_contexts import Lock, Terminal, Dumb

# TODO
class DeviceEventMock(DeviceEventContext):

    def __init__(self, event):
        super().__init(event)


def test_context_sanity_test(fake_message):
    message = fake_message(dev_type='lock')
    with DeviceEventContext(message) as context:
        assert not context.old, 'context too old'
        assert context.model, 'no context model'
        assert context.ts != 0, 'whoops, missing ts'






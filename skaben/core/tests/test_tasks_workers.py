import pytest
from core.tasks import workers

@pytest.fixture
def make_worker(monkeypatch):

    def _wrap(worker_class):
        mock_queue = []

        def pack(*args):
            mock_queue.append(args)

        worker = worker_class(None, None, None)
        monkeypatch.setattr(worker, "publish", pack)

        return worker, mock_queue

    return _wrap


@pytest.fixture
def make_message():

    class MockMessage:
        def __init__(self, routing_key):
            self.delivery_info = {"routing_key": routing_key}

    def _wrap(body, topic):
        return body, MockMessage(topic)

    return _wrap


def test_base_parse_basic(make_worker):
    worker = make_worker(workers.BaseWorker)
    routing_key = "test.my.routing"
    res = worker.parse_basic(routing_key)

    assert res == {"device_type": "test",
                   "device_uid": "my",
                   "command": "routing"}, f"bad result for basic parsing: {res}"

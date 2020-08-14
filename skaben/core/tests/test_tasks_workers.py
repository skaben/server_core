import pytest
from core.tasks import workers

@pytest.fixture
def make_worker(monkeypatch):

    def _wrap(worker_class):
        worker = worker_class(None, None, None)

        return worker

    return _wrap
from core.tasks.workers import WorkerRunner, \
    AckNackWorker, SaveWorker, StateUpdateWorker, \
    PingPongWorker, SendConfigWorker, LogWorker
from core.tasks.recurrent import Pinger
from transport.rabbitmq import connection, pool, exchanges
import transport.queues as tq


WORKERS = []
RECURRENT = {}


worker_processes = dict(
    worker_pong=WorkerRunner(worker_class=PingPongWorker,
                             connection=connection,
                             queues=[tq.pong_queue, ],
                             exchanges=exchanges),

    worker_ack_nack=WorkerRunner(worker_class=AckNackWorker,
                                 connection=connection,
                                 queues=[tq.ack_queue, tq.nack_queue],
                                 exchanges=exchanges),

    worker_cup=WorkerRunner(worker_class=SendConfigWorker,
                            connection=connection,
                            queues=[tq.cup_queue, ],
                            exchanges=exchanges),

    worker_sup=WorkerRunner(worker_class=StateUpdateWorker,
                               connection=connection,
                               queues=[tq.sup_queue, tq.info_queue],
                               exchanges=exchanges),

    worker_save=WorkerRunner(worker_class=SaveWorker,
                            connection=connection,
                            queues=[tq.save_queue, ],
                            exchanges=exchanges),

    worker_logging=WorkerRunner(worker_class=LogWorker,
                                connection=connection,
                                queues=[tq.log_queue, tq.error_queue],
                                exchanges=exchanges)
)


def run_workers():
    try:
        results = []
        for name, proc in worker_processes.items():
            if name not in WORKERS:
                proc.start()
                WORKERS.append(name)
                results.append(f"{name} start")
            else:
                results.append(f"{name} already running")
        return results
    except Exception:
        raise


def run_pinger():
    name = 'pinger'
    result = f'{name} already running'
    try:
        pinger = Pinger()
        if pinger.name not in RECURRENT:
            pinger.start()
            RECURRENT.update({name: pinger})
            result = f'{name} started'
        return result
    except Exception:
        raise


def stop_all():
    try:
        results = []
        for name, proc in worker_processes.items():
            proc.kill()
            WORKERS.pop(WORKERS.index(name))
            results.append(f"terminated worker: {name}")
        names = []
        for name in RECURRENT:
            if RECURRENT.get(name):
                RECURRENT[name].kill()
                names.append(name)
                results.append(f"terminated recurrent task: {name}")
            try:
                RECURRENT.pop(name)
            except Exception:
                pass
        return results
    except Exception:
        raise

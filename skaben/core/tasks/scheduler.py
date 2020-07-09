import asyncio
import multiprocessing as mp
from contextlib import suppress
from concurrent.futures import ProcessPoolExecutor


class Periodic:
    """ periodic async task """
    def __init__(self, func, time):
        self.func = func
        self.time = time
        self.is_started = False
        self._task = None

    async def start(self):
        """ Start task to call func periodically """
        if not self.is_started:
            self.is_started = True
            self._task = asyncio.ensure_future(self._run())

    async def stop(self):
        """ Stop task and await it stopped """
        if self.is_started:
            self.is_started = False
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def _run(self):
        while True:
            await asyncio.sleep(self.time)
            self.func()


class Scheduler(mp.Process):

    loop = None
    running = False
    tasks = {}

    def __init__(self, pool_size=2):
        super().__init__()
        self.loop = asyncio.new_event_loop()
        self.executor = ProcessPoolExecutor(pool_size)
        self.queue = mp.Queue()
        asyncio.set_event_loop(self.loop)

    def add(self, name, function, timeout):
        task = Periodic(function, timeout)
        self.queue.put_nowait(("add", name, task))

    def remove(self, name):
        self.queue.put_nowait(("del", name, ''))

    def run(self):
        self.running = True
        while self.running:
            self.loop.run_until_complete(self.main())

    async def main(self):
        if not self.queue.empty():
            cmd, name, task = self.queue.get()
            if cmd == 'add':
                self.tasks.update({name: task})
            elif cmd == 'del' and self.tasks.get(name):
                task = self.tasks.pop(name, None)
                await task.stop()
        await asyncio.gather(*[task.start() for task in self.tasks.values()])
        await asyncio.sleep(.5)


scheduler = Scheduler()
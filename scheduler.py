# -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from concurrent.futures import wait
from queue import Queue
import time
from threading import Thread


class _WorkItem:

    __slots__ = ["fn", "args", "kwargs"]

    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs


class Scheduler:

    def __init__(self, kind='process', max_workers=None, show_info=False):
        self._events = []
        if kind == 'process':
            self._pool = ProcessPoolExecutor(max_workers=max_workers)
        elif kind == 'thread':
            self._pool = ThreadPoolExecutor(max_workers=max_workers)
        else:
            raise TypeError('unsupported parallel type')
        self._futures = []
        self.process_start = time.time()
        self.queue = Queue()
        self.result_t = Thread(target=self.show_result)
        self.result_t.daemon = True
        if show_info:
            self.result_t.start()

    def register(self, event, *args, **kwargs):
        self._events.append(_WorkItem(event, args, kwargs))

    def _prepare(self):
        for work_item in self._events:
            if not isinstance(work_item.fn, list):
                _future = self._pool.submit(work_item.fn, *work_item.args, **work_item.kwargs)
                _future._fn_name = work_item.fn.__name__
                _future.add_done_callback(self.callback)
                self._futures.append(_future)
            else:
                _future = self._pool.submit(self._order_exe, work_item)
                _future._fn_name = [func.__name__ for func in work_item.fn]
                _future.add_done_callback(self.callback)
                self._futures.append(_future)

    @staticmethod
    def _order_exe(work_item):
        res = []
        for _event in work_item.fn:
            res.append(_event(*work_item.args, **work_item.kwargs))
        return res

    def callback(self, future):
        if future._state == 'FINISHED':
            self.queue.put((future._fn_name, future.result()))
        elif future._state in ['CANCELLED', 'CANCELLED_AND_NOTIFIED']:
            self.queue.put(None)

    def parallel(self):
        self._prepare()
        wait(self._futures)
        for future in self._futures:
            try:
                print((future._fn_name, future.result()))
            except Exception as exc:
                print(f'{future._fn_name} generated an exception: {exc}')

    def serialize(self):
        for work_item in self._events:
            if not isinstance(work_item.fn, list):
                result = work_item.fn(*work_item.args, **work_item.kwargs)
                self.queue.put(result)
            else:
                results = self._order_exe(work_item)
                for result in results:
                    self.queue.put(result)

    def show_result(self):
        while True:
            if not self.queue.empty():
                print('show result: ')
                print(self.queue.get())

    def __del__(self):
        self.process_end = time.time()
        self._pool.shutdown(wait=True)
        # print(f"the process total took {self.process_end - self.process_start} s")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._pool.shutdown(wait=True)
        self.process_end = time.time()
        print(f"the process total time as: {self.process_end - self.process_start} s")

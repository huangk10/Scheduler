# -*- coding: utf-8 -*-

import time
from scheduler import Scheduler

def task_1():
    time.sleep(1)
    a = 1 / 0
    return 1


def task_2():
    time.sleep(2)
    return 2


def task_3():
    time.sleep(2)
    return 3


def task_k(k):
    time.sleep(2)
    return k


if __name__ == '__main__':
    with Scheduler(kind='thread', max_workers=4) as scheduler:
        scheduler.register(task_1)
        scheduler.register([task_2, task_3])
        scheduler.register(task_k, 4)
        scheduler.register([task_k, task_k], 5)
        scheduler.parallel()
        result = scheduler.results()
        print(result)

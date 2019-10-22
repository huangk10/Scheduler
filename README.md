# Scheduler
用concurrent.future实现的易用的并发框架

## Dependency
python 3.x

## Easy to use

```python
with Scheduler() as scheduler:
    scheduler.register(process_one, process_one_args)
    scheduler.register(process_two, process_two_args)
    scheduler.register([process_three, process_four], process_args)
    scheduler.parallel()
```

## How to customize

```python
# 多线程
with Scheduler(kind='thread', max_workers=4) as scheduler:
    ...

# 多进程
with Scheduler(kind='process', max_workers=4) as scheduler:
    ...

# 一般过程
scheduler.register(normal_process, normal_process_args)

# 有前置的过程
scheduler.register([first_process, second_process, ...], processes_common_args)

# 并发执行
scheduler.parallel()

# 顺序执行
scheduler.serilize()

# 结果获取
result = scheduler.results()

```


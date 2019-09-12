ASYNC_TASK_BROKER_URL = "redis://localhost:6379/2"

ASYNC_TASK_TASK_QUEUES = {
    "wd.direct": {
        "exchange": "wd-exchange",
        "exchange_type": "direct",
        "routing_key": "wd.direct",
    }
}

ASYNC_TASK_TASK_DEFAULT_QUEUE = "wd.celery"

ASYNC_TASK_TASK_ROUTES = {
    "app.tasks.*": {"queue": ASYNC_TASK_TASK_DEFAULT_QUEUE}
}

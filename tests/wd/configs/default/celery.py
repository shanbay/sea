CELERY_BROKER_URL = 'redis://localhost:6379/2'

CELERY_TASK_QUEUES = {
    'wd.direct': {
        'exchange': 'wd-exchange',
        'exchange_type': 'direct',
        'routing_key': 'wd.direct',
    },
}

CELERY_TASK_DEFAULT_QUEUE = 'wd.celery'

CELERY_TASK_ROUTES = {
    'app.tasks.*': {
        'queue': CELERY_TASK_DEFAULT_QUEUE,
    },
}

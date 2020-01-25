import celery


class AsyncTask(celery.Celery):
    def init_app(self, app):
        self.config_from_object(app.config.get_namespace("ASYNC_TASK_"))


class Bus(celery.Celery):
    def init_app(self, app):
        self.config_from_object(app.config.get_namespace("BUS_"))

from flask import Flask
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger
from twitter_data_fetch import fetch_data
import warnings
warnings.filterwarnings("ignore")

logger = get_task_logger(__name__)
'''initalizing celery app with configuration'''
def make_celery(app):
    #Celery configuration
    app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
    app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
    app.config['CELERYBEAT_SCHEDULE'] = {
        'periodic_task-every-minute': {
            'task': 'periodic_task',
            'schedule': crontab(minute=1),
        }
    }

    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app = Flask(__name__)
celery = make_celery(app)
'''celery task to fetch the data from twitter API'''
@celery.task(name="periodic_task")
def periodic_task():
    logger.info("fetching twitter data started")
    res = fetch_data()
    logger.info("fetchinng completed")

@app.route('/')
def view():
    return "Hello, Flask is up and running!"

if __name__ == "__main__":
    app.run(debug = True)
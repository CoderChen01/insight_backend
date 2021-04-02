import os

from celery import Celery


# set the default Django settings module for the 'celery' program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insight.settings')

app = Celery('insight_celery')

# load celery's settings from django project settings.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery will auto discover tasks in each app.
app.autodiscover_tasks()

# the debug_task is a task that dumps its own request information
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

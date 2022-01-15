from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accord.settings')

app = Celery("accord")
app.config_from_object("celeryconfig", namespace='CELERY')
app.autodiscover_tasks()
app.conf.timezone = "UTC"


app.conf.beat_schedule = {
    "periodic-analytics-fetch-every-day": {
        "task": "insights.tasks.update_analytics",
        "schedule": crontab(hour='1'),
        "args": ()
    }
}



@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
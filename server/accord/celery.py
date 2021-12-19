from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'accord.settings')

app = Celery("accord")
app.config_from_object("celeryconfig", namespace='CELERY')
app.autodiscover_tasks()
app.conf.timezone = "UTC"


@app.task(bind=True)
def debug_task(self):
    print('Requesy: {0!r}'.format(self.request))
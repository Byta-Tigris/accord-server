import os


CELERY_BROKER_URL = f"ampq://{os.getenv('CELERY_USER', 'jarden')}:{os.getenv('CELERY_PASSWORD', 'krispi@103904')}@{os.getenv('CELERY_HOST_NAME', 'localhost')}:5672/{os.getenv('CELERY_VIRTUAL_HOST', 'accord_host')}"
CELERY_RESULT_BACKEND = f"ampq://{os.getenv('CELERY_USER', 'jarden')}:{os.getenv('CELERY_PASSWORD', 'krispi@103904')}@{os.getenv('CELERY_HOST_NAME', 'localhost')}:5672/{os.getenv('CELERY_VIRTUAL_HOST', 'accord_host')}"
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
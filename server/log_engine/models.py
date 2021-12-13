from django.db import models
import logging

# Create your models here.



class DatabaseLogEntry(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    message = models.TextField()
    is_active = models.BooleanField(default=True)
    level = models.CharField(max_length=10, default='INFO')
    levelno = models.IntegerField(default=logging.INFO)


    class Meta:
        abstract = True


class InfoLogEntry(DatabaseLogEntry):
    pass

class ErrorLogEntry(DatabaseLogEntry):
    pass

class DebugLogEntry(DatabaseLogEntry):
    pass




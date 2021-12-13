from datetime import time
from logging import Handler, LogRecord
import logging

from django.db.models.query_utils import Q
from utils import get_current_time
from .models import DebugLogEntry, InfoLogEntry, ErrorLogEntry



class DatabaseLogHandler(Handler):

    def __init__(self) -> None:
        super(DatabaseLogHandler, self).__init__()
    
    def emit(self, record: LogRecord) -> None:
        print(self.format(record))
        try:
            model = InfoLogEntry
            if record.levelno == logging.DEBUG:
                model = DebugLogEntry
            elif record.levelno > logging.INFO:
                model = ErrorLogEntry
            
            if not model.objects.filter(Q(message=self.format(record)) & Q(levelno=record.levelno)).exists():
                log_entry = model(
                    level = record.levelname,
                    levelno = record.levelno,
                    message=self.format(record),
                    is_active=True,
                    time=get_current_time()                            
                )
                log_entry.save()
        except:
            pass
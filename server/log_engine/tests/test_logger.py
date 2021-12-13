import logging
from django.test import TestCase
from log_engine.log import logger
from log_engine.models import ErrorLogEntry, InfoLogEntry, DebugLogEntry


class TestLogger(TestCase):
    
    def test_logging(self) -> None:
        logger.info("Testing this first time")
        self.assertTrue(InfoLogEntry.objects.exists())
        # Testing Duplication resistance
        logger.info("Testing this first time")
        self.assertEqual(InfoLogEntry.objects.count(), 1)

        # Testing routing
        logger.debug("Debugging this bitch")
        self.assertTrue(DebugLogEntry.objects.exists())
        self.assertFalse(ErrorLogEntry.objects.exists())

        logger.warning("Warning bitch")
        self.assertTrue(ErrorLogEntry.objects.exists())
        entry: ErrorLogEntry = ErrorLogEntry.objects.first()
        self.assertEqual(entry.levelno, logging.WARNING)
        logger.error("Fucking error")
        queryset = ErrorLogEntry.objects.filter(levelno=logging.ERROR)
        self.assertTrue(queryset.exists())
        self.assertEqual(ErrorLogEntry.objects.count(), 2)
        

from django.contrib import admin

from log_engine.models import ErrorLogEntry

# Register your models here.

admin.site.register(ErrorLogEntry)
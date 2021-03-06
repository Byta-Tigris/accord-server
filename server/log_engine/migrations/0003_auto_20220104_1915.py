# Generated by Django 3.2 on 2022-01-04 19:15

from django.db import migrations, models
import utils


class Migration(migrations.Migration):

    dependencies = [
        ('log_engine', '0002_auto_20220104_1915'),
    ]

    operations = [
        migrations.AlterField(
            model_name='debuglogentry',
            name='time',
            field=models.DateTimeField(default=utils.get_current_time),
        ),
        migrations.AlterField(
            model_name='errorlogentry',
            name='time',
            field=models.DateTimeField(default=utils.get_current_time),
        ),
        migrations.AlterField(
            model_name='infologentry',
            name='time',
            field=models.DateTimeField(default=utils.get_current_time),
        ),
    ]

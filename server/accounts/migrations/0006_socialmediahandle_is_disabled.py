# Generated by Django 3.2 on 2022-01-13 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_account_platform_specific_private_metric'),
    ]

    operations = [
        migrations.AddField(
            model_name='socialmediahandle',
            name='is_disabled',
            field=models.BooleanField(default=False),
        ),
    ]

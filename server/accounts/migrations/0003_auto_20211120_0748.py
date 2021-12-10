# Generated by Django 3.2.8 on 2021-11-20 07:48

import datetime
from django.db import migrations, models
import django.db.models.deletion
import django_cryptography.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_account_contact'),
    ]

    operations = [
        migrations.CreateModel(
            name='SocialHandleMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='account',
            name='avatar',
            field=models.URLField(default=''),
        ),
        migrations.AddField(
            model_name='account',
            name='banner_image',
            field=models.URLField(default=''),
        ),
        migrations.AddField(
            model_name='account',
            name='description',
            field=models.TextField(default=''),
        ),
        migrations.AddField(
            model_name='account',
            name='username',
            field=models.CharField(db_index=True, default='', max_length=70, unique=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='created_on',
            field=models.DateTimeField(default=datetime.datetime(2021, 11, 20, 7, 48, 30, 442632)),
        ),
        migrations.CreateModel(
            name='SocialMediaHandle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(db_index=True, default='', max_length=20)),
                ('handle_url', models.URLField()),
                ('media_uid', models.CharField(db_index=True, default='', max_length=255)),
                ('access_token', django_cryptography.fields.encrypt(models.TextField())),
                ('token_expiration_time', models.DateTimeField(default=datetime.datetime(2021, 11, 20, 7, 48, 30, 443499))),
                ('created_on', models.DateTimeField(default=datetime.datetime(2021, 11, 20, 7, 48, 30, 443513))),
                ('username', models.CharField(default='', max_length=70)),
                ('avatar', models.URLField()),
                ('is_publish_permission_valid', models.BooleanField(default=False)),
                ('rates', models.JSONField()),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_handle_account', to='accounts.account')),
            ],
        ),
    ]
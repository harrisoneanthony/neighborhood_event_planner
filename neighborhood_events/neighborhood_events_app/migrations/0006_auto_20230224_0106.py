# Generated by Django 2.2.4 on 2023-02-24 01:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('neighborhood_events_app', '0005_auto_20230224_0104'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='user_id',
            new_name='user',
        ),
    ]

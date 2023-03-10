# Generated by Django 2.2.4 on 2023-02-24 02:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('neighborhood_events_app', '0006_auto_20230224_0106'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attending_event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attending_event', to='neighborhood_events_app.Event')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attending_event', to='neighborhood_events_app.User')),
            ],
        ),
    ]

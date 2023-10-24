# Generated by Django 3.1 on 2021-05-04 13:33

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0014_auto_1454'),
    ]

    operations = [
        migrations.CreateModel(
            name='AsyncTask',
            fields=[
                (
                    'id',
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                (
                    'progress',
                    models.PositiveIntegerField(
                        default=0,
                        validators=[django.core.validators.MaxValueValidator(100)],
                    ),
                ),
                ('is_running', models.BooleanField(default=True)),
                ('result', models.JSONField(null=True)),
                (
                    'user',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.user'),
                ),
            ],
            options={
                'db_table': 'async_tasks',
            },
        ),
    ]

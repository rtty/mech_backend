# Generated by Django

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0005_auto_1647'),
    ]

    operations = [
        migrations.CreateModel(
            name='VinTests',
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
                ('value', models.FloatField()),
                (
                    'project',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='app.Project'
                    ),
                ),
                (
                    'tests',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Test'),
                ),
                (
                    'vin',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Vin'),
                ),
            ],
            options={
                'db_table': 'vin_tests',
            },
        ),
    ]

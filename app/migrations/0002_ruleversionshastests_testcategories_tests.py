# Generated by Django

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestCategories',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80, unique=True)),
            ],
            options={
                'db_table': 'test_categories',
            },
        ),
        migrations.CreateModel(
            name='Tests',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=80)),
                ('type', models.CharField(max_length=80)),
                (
                    'test_categories',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='app.TestCategories',
                    ),
                ),
            ],
            options={
                'db_table': 'tests',
            },
        ),
        migrations.CreateModel(
            name='RuleVersionsHasTests',
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
                (
                    'rule_versions',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to='app.RuleVersion',
                    ),
                ),
                (
                    'tests',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Tests'),
                ),
            ],
            options={
                'db_table': 'rule_versions_has_tests',
            },
        ),
    ]

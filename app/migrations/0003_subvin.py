# Generated by Django

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0002_ruleversionshastests_testcategories_tests'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubVin',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128, unique=True)),
                (
                    'vins',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Vin'),
                ),
            ],
            options={
                'db_table': 'sub_vins',
            },
        ),
    ]

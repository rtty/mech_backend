# Generated by Django 3.1 on 2021-03-11 23:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0010_vintests_qualifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='name',
            field=models.CharField(max_length=80, unique=True),
        ),
        migrations.AlterField(
            model_name='test',
            name='type',
            field=models.CharField(max_length=80, null=True),
        ),
    ]

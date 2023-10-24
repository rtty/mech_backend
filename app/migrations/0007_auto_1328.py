# Generated by Django

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0006_vintests'),
    ]

    operations = [
        migrations.AlterField(
            model_name='test',
            name='name',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterUniqueTogether(
            name='test',
            unique_together={('name', 'type')},
        ),
    ]
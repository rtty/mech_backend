# Generated by Django

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0008_ruleversionnodenote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='name',
            field=models.CharField(max_length=2048),
        ),
    ]
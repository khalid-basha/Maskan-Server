# Generated by Django 4.1.7 on 2023-05-30 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='home',
            name='area',
            field=models.PositiveIntegerField(default=0, help_text='The Area of the house in square foot'),
        ),
    ]

# Generated by Django 3.1.5 on 2021-05-10 01:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_league_test_change'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='league',
            name='test_change',
        ),
    ]
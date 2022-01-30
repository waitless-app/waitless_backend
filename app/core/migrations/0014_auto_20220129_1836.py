# Generated by Django 3.0.14 on 2022-01-29 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_order_pickup_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='accept_time',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='premises',
            name='active',
            field=models.BooleanField(default=False),
        ),
    ]
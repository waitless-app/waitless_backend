# Generated by Django 3.0.14 on 2022-01-15 01:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20210819_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pickup_code',
            field=models.CharField(default=None, editable=False, max_length=10, null=True, unique=True),
        ),
    ]
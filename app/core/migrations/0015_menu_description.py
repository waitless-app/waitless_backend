# Generated by Django 3.0.14 on 2022-03-05 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20220129_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='description',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]
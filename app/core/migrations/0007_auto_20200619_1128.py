# Generated by Django 3.0.5 on 2020-06-19 11:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_premises_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='premises',
            name='owner',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]

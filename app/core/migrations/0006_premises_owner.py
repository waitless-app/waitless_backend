# Generated by Django 3.0.5 on 2020-06-19 11:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_remove_order_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='premises',
            name='owner',
            field=models.ForeignKey(default=1, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
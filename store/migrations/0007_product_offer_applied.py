# Generated by Django 4.2.4 on 2023-09-24 23:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_productsize_offer_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='offer_applied',
            field=models.BooleanField(default=False),
        ),
    ]

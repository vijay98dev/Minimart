# Generated by Django 4.2.4 on 2023-09-24 21:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='categoryoffer',
            name='product',
        ),
    ]
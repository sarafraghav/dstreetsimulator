# Generated by Django 3.2.7 on 2022-04-16 18:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simulator', '0027_auto_20220416_2220'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='news',
            name='stock',
        ),
    ]

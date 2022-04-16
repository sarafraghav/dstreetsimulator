# Generated by Django 3.2.7 on 2022-04-16 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('simulator', '0026_league_trading_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='holdings',
            name='type',
            field=models.CharField(default='Equity', max_length=10000),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='news',
            name='description',
            field=models.TextField(),
        ),
    ]

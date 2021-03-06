# Generated by Django 3.2.7 on 2021-10-19 05:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('simulator', '0011_lauth_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='transfer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PENDING', 'PENDING'), ('ACCEPTED', 'ACCEPTED'), ('DECLINED', 'DECLINED')], max_length=100)),
                ('active', models.BooleanField()),
                ('from_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_from', to=settings.AUTH_USER_MODEL)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer', to='simulator.league')),
                ('stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer', to='simulator.stocks')),
                ('to_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfer_to', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

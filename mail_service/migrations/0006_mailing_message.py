# Generated by Django 4.2 on 2024-05-20 04:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mail_service', '0005_remove_log_success_log_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='mailing',
            name='message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mailings', to='mail_service.message', verbose_name='Сообщение'),
        ),
    ]

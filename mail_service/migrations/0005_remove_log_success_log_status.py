# Generated by Django 4.2 on 2024-05-17 12:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mail_service', '0004_rename_deliveryattempt_log'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='success',
        ),
        migrations.AddField(
            model_name='log',
            name='status',
            field=models.CharField(choices=[('OK', 'Успешно'), ('failed', 'Ошибка')], default='OK', max_length=20, verbose_name='Статус'),
        ),
    ]

from django.contrib import admin
from mail_service.models import Client, Mailing, Log, Message


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'full_name', 'email',)
    list_filter = ('full_name',)
    search_fields = ('email', 'full_name', 'comment')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_datetime', 'frequency', 'status')
    list_filter = ('frequency', 'status')
    search_fields = ('id',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject')
    search_fields = ('id', 'subject')


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'mailing', 'datetime', 'status', 'server_response',)
    list_filter = ('status',)
    search_fields = ('id', 'mailing__id')

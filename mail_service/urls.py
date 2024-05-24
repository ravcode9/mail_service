from django.urls import path
from django.views.decorators.cache import cache_page

from .views import MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView, MailingDeleteView, \
    StartMailingView, StopMailingView, ClientListView, ClientDetailView, ClientCreateView, ClientUpdateView, \
    ClientDeleteView, LogListView

app_name = 'mail_service'

urlpatterns = [
    path('', MailingListView.as_view(), name='mailing_list'),
    path('<int:pk>/', cache_page(60)(MailingDetailView.as_view()), name='mailing_view'),
    path('create/', MailingCreateView.as_view(), name='mailing_create'),
    path('<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailing/<int:pk>/start/', StartMailingView.as_view(), name='mailing_start'),
    path('mailing/<int:pk>/stop/', StopMailingView.as_view(), name='mailing_stop'),
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/<int:pk>/', ClientDetailView.as_view(), name='client_detail'),
    path('clients/create/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/update/', ClientUpdateView.as_view(), name='client_update'),
    path('clients/<int:pk>/delete/', ClientDeleteView.as_view(), name='client_delete'),
    path('log/', LogListView.as_view(), name='log_list'),
    ]

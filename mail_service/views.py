from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.cache import cache
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse

from blog.models import Blog
from .forms import MailingForm, ClientForm, MessageForm, PermMailingForm
from .models import Mailing, Client, Message, Log
from django.conf import settings


class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mail_service:mailing_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        MessageFormset = inlineformset_factory(Mailing, Message, form=MessageForm, extra=1)

        if self.request.POST:
            context['formset'] = MessageFormset(self.request.POST)
        else:
            context['formset'] = MessageFormset()

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['formset']

        if formset.is_valid():
            self.object = form.save(commit=False)
            self.object.owner = self.request.user
            self.object.save()

            formset.instance = self.object
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse('mail_service:mailing_list')


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mail_service/mailing_list.html'
    context_object_name = 'mailings'

    def cache_example(self):
        if settings.CACHE_ENABLED:
            key = 'mailing_list'
            mailing_list = cache.get(key)
            if mailing_list is None:
                mailing_list = Mailing.objects.all()
                cache.set(key, mailing_list)
        else:
            mailing_list = Mailing.objects.all()
        return mailing_list

    def get_queryset(self):
        return self.cache_example()

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        # Данные для статистики
        if self.request.user.is_superuser:
            context_data['all'] = Mailing.objects.count()
            context_data['active'] = Mailing.objects.filter(status='started').count()
            context_data['clients_count'] = Client.objects.count()
        else:
            mailing_list = Mailing.objects.filter(owner=self.request.user)
            context_data['all'] = mailing_list.count()
            context_data['active'] = mailing_list.filter(status='started').count()
            clients = [[client.email for client in mailing.clients.all()] for mailing in mailing_list]
            context_data['clients_count'] = len(clients)

        # Получение случайных статей блога
        if settings.CACHE_ENABLED:
            blog_key = 'random_blogs'
            random_blogs = cache.get(blog_key)
            if random_blogs is None:
                random_blogs = Blog.objects.order_by('?')[:3]
                cache.set(blog_key, random_blogs)
        else:
            random_blogs = Blog.objects.order_by('?')[:3]

        context_data['blogs'] = random_blogs
        return context_data


class MailingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Mailing

    def test_func(self):
        mailing_settings = self.get_object()
        return (self.request.user.is_superuser or self.request.user == mailing_settings.owner or
                self.request.user.has_perm(
                    'mail_service.view_mailingsettings'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.all()
        return context


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy('mail_service:mailing_list')

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.has_perm('mail_service.change_status')

    def get_form_class(self):
        if self.request.user.has_perm('mail_service.change_status') and not self.request.user.is_superuser:
            return PermMailingForm
        return MailingForm

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        MessageFormset = inlineformset_factory(Mailing, Message, extra=1, form=MessageForm)

        if self.request.method == 'POST':
            context_data['formset'] = MessageFormset(self.request.POST, instance=self.object)
        else:
            context_data['formset'] = MessageFormset(instance=self.object)

        return context_data

    def form_valid(self, form):
        formset = self.get_context_data()['formset']
        self.object = form.save()
        if formset.is_valid():
            formset.instance = self.object
            formset.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('mail_service:mailing_detail', args=[self.object.pk])


class MailingDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Mailing
    template_name = 'mail_service/mailing_confirm_delete.html'
    success_url = reverse_lazy('mail_service:mailing_list')

    def test_func(self):
        return self.request.user.is_superuser


class ClientListView(LoginRequiredMixin, ListView):
    model = Client

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Client.objects.all()
        else:
            return Client.objects.filter(owner=self.request.user)


class ClientDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Client

    def test_func(self):
        client = self.get_object()
        return self.request.user.is_superuser or self.request.user == client.owner


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm

    def get_success_url(self):
        return reverse('mail_service:client_list')

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()

        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'mail_service/client_form.html'
    success_url = reverse_lazy('mail_service:client_list')

    def test_func(self):
        client = self.get_object()
        return self.request.user.is_superuser or self.request.user == client.owner


class ClientDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('mail_service:client_list')

    def test_func(self):
        client = self.get_object()
        return self.request.user.is_superuser or self.request.user == client.owner


class StartMailingView(View):
    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        if mailing.status == 'created':
            mailing.status = 'started'
            mailing.save()
            messages.success(request, 'Рассылка успешно запущена.')
        else:
            messages.error(request, 'Эту рассылку нельзя запустить.')
        return redirect('mail_service:mailing_list')


class StopMailingView(View):
    def get(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        return render(request, 'mail_service/mailing_detail.html', {'mailing': mailing})

    def post(self, request, pk):
        mailing = get_object_or_404(Mailing, pk=pk)
        if mailing.status == 'started':
            mailing.status = 'completed'
            mailing.save()
            messages.success(request, 'Рассылка успешно завершена.')
        else:
            messages.error(request, 'Эту рассылку нельзя завершить.')
        return redirect('mail_service:mailing_list')


class LogListView(LoginRequiredMixin, ListView):
    """Просмотр списка логов"""
    model = Log

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        user = self.request.user
        mailing_list = Mailing.objects.filter(owner=user).first()
        if user.is_superuser:
            context_data['all'] = Log.objects.count()
            context_data['success'] = Log.objects.filter(
                status=True).count()
            context_data['error'] = Log.objects.filter(status=False).count()
        else:
            user_logs = Log.objects.filter(mailing_list=mailing_list)
            context_data['all'] = user_logs.count()
            context_data['success'] = user_logs.filter(
                status=True).count()
            context_data['error'] = user_logs.filter(status=False).count()
        return context_data

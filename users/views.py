import random
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.views.generic import CreateView, UpdateView, TemplateView, FormView, ListView
from config import settings
from config.settings import EMAIL_HOST_USER
from users.forms import UserRegisterForm, UserProfileForm, PermUserForm
from users.models import User
from .forms import PasswordRecoveryForm


class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:register_message')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = "".join([str(random.randint(0, 9)) for i in range(10)])
        user.token = token
        current_host = self.request.get_host()
        user.save()
        send_mail("Регистрация на сайте!", f"""Подтвердите свой профиль, перейдя по ссылке\n
    {current_host}/users/register/confirm/{token}/""", EMAIL_HOST_USER, [user.email])
        return super().form_valid(form)


class UserUpdateView(UpdateView):
    model = User
    success_url = reverse_lazy('users:profile')
    form_class = UserProfileForm

    def get_object(self, queryset=None):
        return self.request.user


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserRegisterMessageView(TemplateView):
    template_name = 'users/register_message.html'


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    return HttpResponseRedirect('/users/login/')


class UserPasswordRecoveryView(FormView):
    template_name = 'users/password_recovery.html'
    form_class = PasswordRecoveryForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        else:
            new_password = get_random_string(length=12)
            user.password = make_password(new_password)
            user.save()
            send_mail(
                'Восстановление пароля',
                f'Ваш новый пароль: {new_password}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

        messages.success(self.request, 'На вашу почту выслано сообщение о восстановлении пароля.')

        return super().form_valid(form)


class UserListView(PermissionRequiredMixin, ListView):
    model = User
    permission_required = 'users.view_user'


class UserMngUpdateView(UpdateView):
    model = User
    success_url = reverse_lazy('users:users')
    form_class = PermUserForm

    def get_queryset(self):
        return User.objects.filter(is_superuser=False)

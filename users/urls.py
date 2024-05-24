from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.apps import UsersConfig
from users.views import UserRegisterView, UserProfileView, email_verification, UserRegisterMessageView, \
    UserPasswordRecoveryView, \
    UserListView, UserMngUpdateView

app_name = UsersConfig.name


urlpatterns = [
    path('login/', LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('register/confirm/<str:token>/', email_verification, name='email_verification'),
    path('register/message/', UserRegisterMessageView.as_view(), name='register_message'),
    path('password_recovery/', UserPasswordRecoveryView.as_view(), name='password_recovery'),
    path('users/', UserListView.as_view(), name='users'),
    path('users/<int:pk>', UserMngUpdateView.as_view(template_name='users/user_update.html'), name='user_update'),
]



from django.urls import path
from user.views import (
    CloseUser,
    ForgotPasswordView,
    IsExpired,
    LoginView,
    RegisterView,
    SendEmailCaptcha,
    UpdateEmailView,
    UpdatePasswordView,
)

urlpatterns = [
    path("login", LoginView.as_view()),
    path("register", RegisterView.as_view()),
    path("send-email-captcha", SendEmailCaptcha.as_view()),
    path("update-password", UpdatePasswordView.as_view()),
    path("forgot-password", ForgotPasswordView.as_view()),
    path("update-email", UpdateEmailView.as_view()),
    path("destroy-user", CloseUser.as_view()),
    path("is-expired", IsExpired.as_view()),
]

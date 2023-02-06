# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from .views import login_view, register_user, ActivateAccount
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', login_view, name="login"),
    path('register/', register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),

    path('activate/<uidb64>/<token>/', ActivateAccount.as_view(), name='activate'),

    # Reset Password URLs
    path('reset_password/', auth_views.PasswordResetView.as_view(template_name='accounts/password_reset.html'), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_sent.html'), name="password_reset_done"),
    path('reset_password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_form.html'), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name="password_reset_complete"),

]

# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from . import views

urlpatterns = [
    ### Training Module
    path('dashboard/management/users/', views.dashboard_management_user, name="dashboard_management_user"),
    path('dashboard/management/users/<str:id>/', views.dashboard_management_user_id, name="dashboard_management_user_id"),
    path('dashboard/management/users_delete/<str:id>/', views.dashboard_management_user_id_delete, name="dashboard_management_user_id_delete"),

]

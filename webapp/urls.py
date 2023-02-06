# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from . import views

urlpatterns = [

    ### Webapp Module
    path('webapp/', views.webapp_home, name="webapp_home"),
    path('webapp/login/', views.webapp_login, name="webapp_login"),
]

# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path
from . import views

urlpatterns = [

    ### Claim Module
    path('dashboard/claim/<str:role>/dashboard/', views.dashboard_claim_dashboard, name="dashboard_claim_dashboard"),
    path('dashboard/claim/<str:role>/category/<str:category>/', views.dashboard_claim_project_list, name="dashboard_claim_project_list"),
    path('dashboard/claim/<str:role>/category/<str:category>/<str:id>/', views.dashboard_claim_application, name="dashboard_claim_application"),
    
    path('dashboard/claim/<str:role>/review/list/', views.dashboard_claim_review_list, name="dashboard_claim_review_list"),
    path('dashboard/claim/<str:role>/review/id/<str:id>/<str:mode>/', views.dashboard_claim_review, name="dashboard_claim_review"),
    # path('dashboard/claim/list/mileage/', views.dashboard_claim_list_mileage, name="dashboard_claim_list_mileage"),
    # path('dashboard/claim/list/fi/', views.dashboard_claim_list_fi, name="dashboard_claim_list_fi"),
    # path('dashboard/claim/list/tranport/', views.dashboard_claim_list_transport, name="dashboard_claim_list_transport"),
    # path('dashboard/claim/list/accommodation/', views.dashboard_claim_list_accommodation, name="dashboard_claim_list_accommodation"),
    # path('dashboard/claim/list/other/', views.dashboard_claim_list_other, name="dashboard_claim_list_other"),
]

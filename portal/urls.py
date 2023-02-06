# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from . import views

urlpatterns = [
    # Admin Profile
    path('dashboard/', views.dashboard, name="dashboard"),
    path('dashboard/profile/', views.dashboard_profile, name="dashboard_profile"),
    path("search/project/", views.SearchProjectResultsView.as_view(), name="search_project_results"),
    path("search/company/", views.SearchCompanyResultsView.as_view(), name="search_company_results"),
    path('dashboard/profile/work-experience/<str:id>', views.dashboard_profile_work_experience, name="dashboard_profile_work_experience"),
    path('dashboard/profile/academic-qualification/<str:id>', views.dashboard_profile_academic_qualification, name="dashboard_profile_academic_qualification"),
    
    # Admin Portal
    path('dashboard/announcement/', views.dashboard_announcement, name="dashboard_announcement"),
    path('dashboard/announcement/<str:id>/', views.dashboard_announcement_id, name="dashboard_announcement_id"),
    path('dashboard/publication/', views.dashboard_publication, name="dashboard_publication"),
    path('dashboard/publication/<str:id>', views.dashboard_publication_id, name="dashboard_publication_id"),
    path('dashboard/training/', views.dashboard_training, name="dashboard_training"),
    path('dashboard/training/<str:id>', views.dashboard_training_id, name="dashboard_training_id"),
    #path('dashboard/user/', views.dashboard_user, name="dashboard_user"),

    path('certificate/role-application/<str:id>/', views.certificate_role_application, name="certificate_role_application"),
    path('certificate/qia/<str:id>/', views.certificate_qia, name="certificate_qia"),

    path('dashboard/update/info/', views.updatelogoview, name='update_info'),
    path('dashboard/update/hyperlink/', views.updatehyperlinkview, name='update_hyperlink'),
    path('dashboard/application/history/', views.applicationhistoryview, name='application_history'),

    path('dashboard/update/footer/info/', views.updateinfoview, name='update_info_footer'),
    

    path('dashboard/graph/', views.dashboardgrpahview, name="dashboard_graph"),
]

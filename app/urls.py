# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from app import views, views_pdf

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('assessment/', views.assessment, name='assessment'),
    path('training/', views.training, name='training'),
    path('contact/', views.contact, name='contact'),
    
    path('announcement/detail/<str:id>/', views.announcement, name='announcement'),
    path('publication/detail/<str:id>/', views.publication, name='publication'),

    # Admin Reporting & Certification
    path('dashboard/report/list/', views.dashboard_report_list, name="dashboard_report_list"),
    path('dashboard/report/view/<str:report_type>/<str:id>/', views.dashboard_qlassic_report_view, name="dashboard_qlassic_report_view"),
    path('dashboard/report/casc_approve/<str:report_type>/<str:id>/', views.dashboard_report_casc_approve, name="dashboard_report_casc_approve"),
    path('dashboard/report/review/<str:report_type>/<str:id>/', views.dashboard_report_review, name="dashboard_report_review"),
    path('dashboard/report/verify/<str:report_type>/<str:id>/', views.dashboard_report_verify, name="dashboard_report_verify"),
    path('dashboard/report/approve/<str:report_type>/<str:id>/', views.dashboard_report_approve, name="dashboard_report_approve"),
    path('dashboard/report/submit/<str:report_type>/<str:id>/', views.dashboard_report_submit, name="dashboard_report_submit"),

    path('dashboard/report/assessment_detail/<str:id>/', views.assessment_report_detail, name="dashboard_assessment_detail"),
    path('dashboard/report/assessment_detail_ef/<str:id>/', views.assessment_report_detail_ef, name="dashboard_assessment_detail_ef"),
    path('dashboard/report/assessment_detail_ew/<str:id>/', views.assessment_report_detail_ew, name="dashboard_assessment_detail_ew"),

    path('dashboard/report/assessment_detail_result/<str:id>/', views.assessment_report_detail_result, name="dashboard_assessment_detail_result"),
    path('dashboard/report/attendance_detail/<str:id>/', views.assessment_attendance_detail, name="dashboard_attendance_detail"),

    
    # PDF
    # path('report/<str:report_type>/view/<str:id>/', views.qlassic_report_generate, name="qlassic_report_generate"),
    path('report/<str:report_type>/generate/<str:id>/', views.report_generate, name="report_generate"),
    # path('report/generate/test/', views_pdf.report_generate_test, name="report_generate_test"),

    path('reportpdf_certificate/<str:id>/', views.getPdfCertificate, name="get pdf"),
    path('reportpdf_score/<str:id>/', views.getPdfScore, name="get pdf"),


    # Admin Management
    path('dashboard/management/defect_group/', views.dashboard_defect_group, name="dashboard_defect_group"),
    path('dashboard/management/defect_group/<str:id>/', views.dashboard_defect_group_id, name="dashboard_defect_group_id"),
    path('dashboard/management/sub-component/', views.dashboard_sub_component, name="dashboard_sub_component"),
    path('dashboard/management/sub-component/<str:id>/', views.dashboard_sub_component_id, name="dashboard_sub_component_id"),
    path('dashboard/management/component/', views.dashboard_component, name="dashboard_component"),
    path('dashboard/management/component/<str:id>/', views.dashboard_component_id, name="dashboard_component_id"),
    path('dashboard/management/element/', views.dashboard_element, name="dashboard_element"),
    path('dashboard/management/element/<str:id>/', views.dashboard_element_id, name="dashboard_element_id"),
    path('dashboard/management/verified-contractor/', views.dashboard_verified_contractor, name="dashboard_verified_contractor"),
    path('dashboard/management/verified-contractor/<str:id>/', views.dashboard_verified_contractor_id, name="dashboard_verified_contractor_id"),
    path('dashboard/management/letter-template/', views.dashboard_letter_template, name="dashboard_letter_template"),
    path('dashboard/management/letter-template/<str:id>', views.dashboard_letter_template_id, name="dashboard_letter_template_id"),
    path('dashboard/management/training-type/', views.dashboard_training_type, name="dashboard_training_type"),
    path('dashboard/management/training-type/<str:id>', views.dashboard_training_type_id, name="dashboard_training_type_id"),

    path('dashboard/management/component-v2/list/', views.dashboard_manage_component_v2, name="dashboard_manage_component_v2"),
    path('dashboard/management/component-v2/list/<str:mode>/<str:id>/', views.dashboard_manage_sub_component_v2, name="dashboard_manage_sub_component_v2"),
    path('dashboard/management/component-v2/edit/<str:mode>/<str:id>/', views.dashboard_manage_edit_component_v2, name="dashboard_manage_edit_component_v2"),

    # path('pdf/generate/<str:report_type>/', views_pdf.report_generate, name='report_view'),
    # path('pdf/view/<str:report_type>/', views_pdf.report_edit, name='generate_view'),
    # path('test/email/', views.test_email, name="test_email"),
    # Matches any html file
    # re_path(r'^.*\.*', views.pages, name='pages'),

    # Test anythong here
    path('sandbox/', views.sandbox, name='sandbox'),
]

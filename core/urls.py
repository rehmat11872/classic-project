# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from django.urls import path, include  # add this
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),          # Django admin route
    path('admin' , admin.site.urls),          # Django admin route 
    path("", include("authentication.urls")), # Auth routes - login / register
    path("", include("app.urls")),            # General
    path("", include("portal.urls")),         # Portal
    path("", include("assessments.urls")),    # Assessments
    path("", include("billings.urls")),       # Billing/Claim
    path("", include("trainings.urls")),      # Trainings
    path("", include("users.urls")),          # Users
    path("", include("webapp.urls")),         # Webapp
    
    path("", include("api.urls")),            # API
]
if settings.AWS_ACCESS_KEY_ID == '':
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

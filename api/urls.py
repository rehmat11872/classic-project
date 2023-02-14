from django.conf import settings
from django.conf.urls import include, url
from django.urls import path
# from django.contrib.gis import admin

from rest_framework import routers
from rest_framework_extensions.routers import NestedRouterMixin

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

from users.views_api import (
    MyTokenObtainPairView
)

class NestedDefaultRouter(NestedRouterMixin, routers.DefaultRouter):
    pass

router = NestedDefaultRouter()

# Users app
from users.views_api import (
    CustomUserViewSet,
    AssessorViewSet
)
users_router = router.register(
    'users', CustomUserViewSet
)
users_router = router.register(
    'assessors', AssessorViewSet
)
# Is Alive
from users.views_api import (
    IsAliveView,
    ReadySyncView,
    ReadyCompleteView,
    GetDocumentView,
    # LoginView,
)

# Assesssments App
from assessments.views_api import (
    AssignedAssessorViewSet,
    AssessmentDataViewSet,
    GetProjectDataView,
    SyncView,
    OverviewView,
    CompleteView,
    GetAgreementView,
    AppNoView
)
assessors_router = router.register(
    'assigend_assessor', AssignedAssessorViewSet
)
assessors_router = router.register(
    'assessment_data', AssessmentDataViewSet
)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # REST
    url('api/v1/isAlive', IsAliveView.as_view(), name='isAlive'),
    url('api/v1/getProjectData', GetProjectDataView.as_view(), name='api_get_project_data'),
    url('api/v1/sync', SyncView.as_view(), name='api_sync'),
    url('api/v1/complete', CompleteView.as_view(), name='api_complete'),
    path('api/v1/readySync/<str:id>', ReadySyncView.as_view(), name='readySync'),
    path('api/v1/readyComplete/<str:id>', ReadyCompleteView.as_view(), name='readyComplete'),
    path('api/v1/getDocument/<str:id>', GetDocumentView.as_view(), name='getDocument'),
    path('api/v1/overview/<str:projectID>', OverviewView.as_view(), name='api_overview'),
    path('api/v1/getAgreement/<str:projectID>', GetAgreementView.as_view(), name='api_getAgreement'),
    path('api/v1/appNo/<str:projectID>', AppNoView.as_view(), name='api_appNo'),
    
    url(r'api/v1/', include(router.urls)),
    url(r'auth/', include('rest_auth.urls')),
    url(r'auth/registration/', include('rest_auth.registration.urls')),
    # url(r'auth/login/', LoginView.as_view(), name='api_login'),
    url('api/v1/auth/obtain', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    url('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    url('auth/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# CRON JOBS
from api.schedulers import start_jobs
start_jobs()
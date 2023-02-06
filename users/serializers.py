from assessments.serializers import AssessmentDataSerializer
from datetime import datetime
from calendar import timegm
import json

from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework import serializers
from django.utils.timezone import now
#from api.settings import AWS_S3_ENDPOINT_URL, AWS_STORAGE_BUCKET_NAME

from .models import (
    CustomUser,
    Assessor,
)

from assessments.models import (
    AssessmentData,
)

from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import update_last_login

# class UserLoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(max_length=128, write_only=True)
#     access = serializers.CharField(read_only=True)
#     refresh = serializers.CharField(read_only=True)
#     role = serializers.CharField(read_only=True)

#     def validate(self, data):
#         email = data['email']
#         password = data['password']
#         user = authenticate(email=email, password=password)

#         if user is None:
#             raise serializers.ValidationError("Invalid login credentials")

#         try:
#             refresh = RefreshToken.for_user(user)
#             refresh_token = str(refresh)
#             access_token = str(refresh.access_token)

#             update_last_login(None, user)

#             validation = {
#                 'access': access_token,
#                 'refresh': refresh_token,
#                 'email': user.email,
#                 'role': user.role,
#             }

#             return validation
#         except CustomUser.DoesNotExist:
#             raise serializers.ValidationError("Invalid login credentials")

# class LoginSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(
#         max_length=65, min_length=8, write_only=True)
#     email = serializers.EmailField(max_length=255, min_length=2)

#     class Meta:
#         model = CustomUser
#         fields = ['email', 'password']

class CustomUserSerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField('get_project')
    class Meta:
        model = CustomUser
        fields = (
            'name', 
            'email', 
            'created_date',
            'is_active',
            'projects',
        )
        read_only_fields = ('email', 'id')

    def get_project(self, obj):
        projects = AssessmentData.objects.all()
        serialized = AssessmentDataSerializer(projects.data)
        return serialized


class AssessorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Assessor
        fields = (
            'user', 
            'assessor_no', 
            'created_date'
        )
        read_only_fields = ('email', 'id')


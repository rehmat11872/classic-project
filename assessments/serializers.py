from django.urls import path, include
from rest_framework import routers, serializers, viewsets

from assessments.models import QlassicAssessmentApplication, AssignedAssessor, AssessmentData
from users.models import CustomUser
from projects.models import ProjectInfo

class AssignedAssessorSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedAssessor
        fields = '__all__'
        # read_only_fields = ('email', 'id')

class AssessmentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentData
        fields = '__all__'
        # read_only_fields = ('email', 'id')

class QlassicAssessmentApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QlassicAssessmentApplication
        fields = '__all__'
        # read_only_fields = ('email', 'id')

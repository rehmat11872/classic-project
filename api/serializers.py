from django.urls import path, include
from rest_framework import routers, serializers, viewsets

from assessments.models import QlassicAssessmentApplication
from users.models import CustomUser
from projects.models import ProjectInfo

# Serializers define the API representation.

# alternative: serializers.HyperlinkedModelSerializer

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name','email','get_role_display']

class QlassicScoreSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = QlassicAssessmentApplication
        fields = ['id','user','qaa_number','qlassic_score','application_status','get_application_status_display','created_date']
        url_field_name = 'qlassic-score'
        read_only_fields = ('id',)

class QlassicInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = QlassicAssessmentApplication
        fields = '__all__'
        url_field_name = 'qlassic-information'

class ProjectInfoSerializer(serializers.ModelSerializer):
    qaa = QlassicInformationSerializer()
    class Meta:
        model = ProjectInfo
        fields = '__all__'



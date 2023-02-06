from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         data = super().validate(attrs)
#         if self.user.is_authenticated:
#             data['authentication_status'] = 'Authenticated'
#         else:
#             data['authentication_status'] = 'No'
#         refresh = self.get_token(self.user)
#         data['refresh'] = str(refresh)
#         data['access'] = str(refresh.access_token)

#         # Add extra responses here
#         data['name'] = self.user.name
#         data['nric'] = self.user.icno
#         data['role'] = self.user.role
#         data['token'] = str(refresh.access_token)
#         data['status'] = 'success'
#         data['projects'] = []
#         return data

#     @classmethod
#     def get_token(cls, user):
#         token = super().get_token(user)
#         token['email'] = user.email
#         token['role'] = user.role
#         return token


from django.contrib.auth import authenticate
from rest_framework import serializers, status
from django.http import Http404
from assessments.models import AssignedAssessor, QlassicAssessmentApplication, SupportingDocuments
from assessments.helpers import get_qaa_sd_name
from assessments.serializers import (
    AssignedAssessorSerializer
)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        user = authenticate(username=attrs['email'], password=attrs['password'])
        if user is not None:
            #if user.is_active and user.is_assessor():
            if user.is_active:
                data = super().validate(attrs)
                refresh = self.get_token(self.user)
                refresh['username'] = self.user.email
                # try:
                access_token = str(refresh.access_token)
                data["refresh"] = str(refresh)
                data["access"] = access_token

                
                # Add extra responses here
                data['name'] = self.user.name
                data['email'] = self.user.email
                data['nric'] = self.user.icno
                data['role'] = self.user.role
                data['token'] = access_token
                data['status'] = 'success'
                # print(type(data))
                data['project'] = []
                # projects = AssignedAssessor.objects.all().filter(assessor__user=user).values()
                # data['projects'] = list(projects)
                projects = AssignedAssessor.objects.all().filter(assessor__user=user,complete=False)
                
                for project in projects:
                    qaa = project.ad.qaa
                    assessors = AssignedAssessor.objects.all().filter(ad=project.ad)
                    
                    lead_assessor = assessors.filter(role_in_assessment='lead_assessor').first()


                    try:                    
                        if qaa.application_status != 'verified':
                            project_json = {
                                'name': qaa.pi.project_title,
                                'id': qaa.id,
                                'code': qaa.qaa_number,
                                'status': 'On-Going',
                                'phase': 'On-Going',
                                'location': qaa.pi.project_location,
                                'sample': project.ad.calculate_sample(),
                                'days': qaa.no_of_days,
                                'date': qaa.assessment_date,
                                'leadName': lead_assessor.assessor.user.name,
                                'leadNric': lead_assessor.assessor.user.icno,
                                'assessors': [],
                            }
                            for assessor in assessors:
                                assessor_json = {
                                    'name': assessor.assessor.user.name,
                                    'nric': assessor.assessor.user.icno
                                }
                                project_json['assessors'].append(assessor_json)

                            data['project'].append(project_json)
                    except Exception as e:
                        print(e)
                            
                    # for project in projects:
                    #     data.update({'projects':project.ad})
                
                # except Exception as e:
                #     data = {
                #         'description': 'Data Error',
                #         'status': 'failed'
                #     }
                #     return data
                return data
            else:
                data = {
                    'description': 'Invalid email or password',
                    'status': 'failed'
                }
                return data
        else:
            data = {
                'description': 'Invalid email or password',
                'status': 'failed'
            }
            return data
            # raise serializers.ValidationError('Incorrect userid/email and password combination!')


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    
from django.shortcuts import render
from django.db.models import Q

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework import viewsets, status
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView

from django_filters.rest_framework import DjangoFilterBackend

from users.models import (
    CustomUser,
    Assessor,
)

from users.serializers import (
    CustomUserSerializer,
    AssessorSerializer,
)

# class UserLoginView(APIView):
#     serializer_class = UserLoginSerializer
#     permission_classes = (AllowAny, )

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         valid = serializer.is_valid(raise_exception=True)

#         if valid:
#             status_code = status.HTTP_200_OK

#             response = {
#                 'success': True,
#                 'statusCode': status_code,
#                 'message': 'User logged in successfully',
#                 'access': serializer.data['access'],
#                 'refresh': serializer.data['refresh'],
#                 'authenticatedUser': {
#                     'email': serializer.data['email'],
#                     'role': serializer.data['role']
#                 }
#             }

#             return Response(response, status=status_code)

# from django.contrib import auth
# import jwt
# from django.conf import settings
# class LoginView(GenericAPIView):
#     serializer_class = LoginSerializer

#     def post(self, request):
#         data = request.data
#         email = data.get('email', '')
#         password = data.get('password', '')
#         user = auth.authenticate(username=email, password=password)
#         if user:
#             print('authenticated ddd')
#             auth_token = jwt.encode(
#                 # {'username': user.username}
#                 {'username': user.email}
#             , settings.JWT_SECRET_KEY)

#             serializer = CustomUserSerializer(user)

#             data = {
#                 'user': serializer.data,
#                 'token': auth_token,
#                 'status': True,
#             }

#             return Response(data, status=status.HTTP_200_OK)

#             # SEND RES
#         return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class CustomUserViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = [
        'role',
        'is_active'
    ]

    def get_permissions(self):
        if self.action == 'list':
            # permission_classes = [IsAuthenticated] #AllowAny IsAuthenticated
            permission_classes = [AllowAny] #AllowAny IsAuthenticated
        else:
            # permission_classes = [IsAuthenticated]
            permission_classes = [AllowAny] #AllowAny IsAuthenticated

        return [permission() for permission in permission_classes]    

    
    def get_queryset(self):
        queryset = CustomUser.objects.all().filter()

        """
        if self.request.user.is_anonymous:
            queryset = Company.objects.none()

        else:
            user = self.request.user
            company_employee = CompanyEmployee.objects.filter(employee=user)
            company = company_employee[0].company
            
            if company.company_type == 'AD':
                queryset = User.objects.all()
            else:
                queryset = User.objects.filter(company=company.id)
        """
        return queryset    
 
class AssessorViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = Assessor.objects.all()
    serializer_class = AssessorSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = [
        'user',
        'assessor_no'
    ]

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated] #AllowAny IsAuthenticated
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]    

    
    def get_queryset(self):
        queryset = Assessor.objects.all().filter()

        """
        if self.request.user.is_anonymous:
            queryset = Company.objects.none()

        else:
            user = self.request.user
            company_employee = CompanyEmployee.objects.filter(employee=user)
            company = company_employee[0].company
            
            if company.company_type == 'AD':
                queryset = User.objects.all()
            else:
                queryset = User.objects.filter(company=company.id)
        """
        return queryset    
 
class IsAliveView(APIView):
    def get_permissions(self):
        permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]    
 
    def get(self, request):
        content = {'status': 'OK'}
        return Response(content, status=status.HTTP_200_OK)
 
# class GetDocumentView(APIView):
#     def get_permissions(self):
#         permission_classes = [AllowAny]

#         return [permission() for permission in permission_classes]    
 
#     def get(self, request, id):
#         content = {'status': 'OK'}
#         return Response(content, status=status.HTTP_200_OK)

class GetDocumentView(APIView):
    def get_permissions(self):
        permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]    
    
    def get_object(self, id):
        try:
            return QlassicAssessmentApplication.objects.get(id=id)
        except QlassicAssessmentApplication.DoesNotExist:
            raise Http404

    def get(self, request, id):
        context = []
        try:
            qaa = self.get_object(id=id)
            documents = SupportingDocuments.objects.all().filter(qaa=qaa)
            print(documents)
            for doc in documents:
                doc_json = {
                    'id': doc.id,
                    'name': get_qaa_sd_name(doc.file_name) + " (Original)",
                    'link': doc.file.url
                }
                context.append(doc_json)
                if doc.reviewed_file != None:
                    try: 
                        doc_json = {
                            'id': doc.id,
                            'name': get_qaa_sd_name(doc.file_name) + " (Reviewed)",
                            'link': doc.reviewed_file.url
                        }
                        context.append(doc_json)
                    except Exception as e:
                        print(e)
                        pass

        except QlassicAssessmentApplication.DoesNotExist:
            context = []
        return Response(context)

class ReadySyncView(APIView):
    def get_permissions(self):
        permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]    
 
    def get(self, request, id):
        context = {}
        try:
            qaa = QlassicAssessmentApplication.objects.get(id=id)
            context = {'readySync': 'OK'}
        except QlassicAssessmentApplication.DoesNotExist:
            context = {'readySync': 'NOT OK'}
        return Response(context, status=status.HTTP_200_OK)

class ReadyCompleteView(APIView):
    def get_permissions(self):
        permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]    
 
    def get(self, request, id):
        context = {}
        try:
            qaa = QlassicAssessmentApplication.objects.get(id=id)
            context = {'readyComplete': 'OK'}
        except QlassicAssessmentApplication.DoesNotExist:
            context = {'readyComplete': 'NOT OK'}
        return Response(context, status=status.HTTP_200_OK)



# class UserLoginView(APIView):
#     serializer_class = UserLoginSerializer
#     permission_classes = (AllowAny, )

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         valid = serializer.is_valid(raise_exception=True)

#         if valid:
#             status_code = status.HTTP_200_OK

#             response = {
#                 'success': True,
#                 'statusCode': status_code,
#                 'message': 'User logged in successfully',
#                 'access': serializer.data['access'],
#                 'refresh': serializer.data['refresh'],
#                 'authenticatedUser': {
#                     'email': serializer.data['email'],
#                     'role': serializer.data['role']
#                 }
#             }

#             return Response(response, status=status_code)

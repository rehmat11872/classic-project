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
from django.core.exceptions import ObjectDoesNotExist

from django_filters.rest_framework import DjangoFilterBackend

from assessments.models import (
    AssignedAssessor, 
    AssessmentData, 
    QlassicAssessmentApplication,
    SampleResult,
    ElementResult,
    SyncResult,
    WorkCompletionForm,
    SiteAttendance,
)

from users.models import Assessor

from assessments.serializers import (
    AssignedAssessorSerializer,
    AssessmentDataSerializer,
    QlassicAssessmentApplicationSerializer,
)

import datetime

class AssignedAssessorViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = AssignedAssessor.objects.all()
    serializer_class = AssignedAssessorSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated] #AllowAny IsAuthenticated
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]    

    
    def get_queryset(self):
        queryset = AssignedAssessor.objects.all().filter()
        return queryset    
 
class AssessmentDataViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = AssessmentData.objects.all()
    serializer_class = AssessmentDataSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated] #AllowAny IsAuthenticated
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]    

    
    def get_queryset(self):
        queryset = AssessmentData.objects.all().filter()
        return queryset

class QlassicAssessmentApplicationViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = QlassicAssessmentApplication.objects.all()
    serializer_class = QlassicAssessmentApplicationSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [IsAuthenticated] #AllowAny IsAuthenticated
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]    

    
    def get_queryset(self):
        queryset = QlassicAssessmentApplication.objects.all().filter()
        return queryset

from assessments.models import (
    Component,
    SubComponent,
    Element,
    DefectGroup,
)

class GetProjectDataView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        data = request.data
        id = data['projectID']
        print(id)
        ad = AssessmentData.objects.get(qaa__id=id)
        response = []
        
        components = Component.objects.all().order_by('created_date')
        sub_components = SubComponent.objects.all().order_by('created_date')
        elements = Element.objects.all().order_by('created_date')
        defect_groups = DefectGroup.objects.all().order_by('created_date')
        for component in components:
            c_json = {
                'category': component.name,
                'type': component.type,
                'items': []
            }
            for sub_component in sub_components:
                if sub_component.component == component:
                    sc_json = {}
                    if component.type == 1:
                        if sub_component.type == 2:
                            sc_json = {
                                'topic': sub_component.name,
                                'type': sub_component.type,
                                'items': []
                            }
                            sc2_json = {
                                'topic': sub_component.name,
                                'subtopics': []
                            }
                            for element in elements:
                                if element.sub_component == sub_component:
                                    el_json = {
                                        'subtopic':element.name,
                                        'id':element.code_id,
                                        'sample':element.no_of_check,
                                        'checkbox':[]
                                    }
                                    for defect_group in defect_groups:
                                        if defect_group.element == element:
                                            el_json['checkbox'].append(defect_group.name)
                                    sc2_json['subtopics'].append(el_json)
                            sc_json['items'].append(sc2_json)

                        if sub_component.type == 3:
                            sc_json = {
                                'topic': sub_component.name,
                                'type': sub_component.type,
                                'ptotal': ad.get_ptotal(),
                                'ctotal': ad.get_ctotal(),
                                'stotal': ad.get_stotal(),
                                'subtopics': []
                            }
                            for element in elements:
                                if element.sub_component == sub_component:
                                    el_json = {
                                        'subtopic':element.name,
                                        'id':element.code_id,
                                        'sample':element.no_of_check,
                                        'checkbox':[]
                                    }
                                    for defect_group in defect_groups:
                                        if defect_group.element == element:
                                            el_json['checkbox'].append(defect_group.name)
                                    sc_json['subtopics'].append(el_json)
                        if sub_component.type != 0:
                            c_json['items'].append(sc_json)
                    if component.type == 2:
                        sc_json = {
                            'topic': sub_component.name,
                            'subtopics': []
                        }
                        for element in elements:
                            if element.sub_component == sub_component:
                                el_json = {
                                    'subtopic':element.name,
                                    'id':element.id,
                                    'sample':element.no_of_check,
                                    'checkbox':[]
                                }
                                for defect_group in defect_groups:
                                    if defect_group.element == element:
                                        el_json['checkbox'].append(defect_group.name)
                                sc_json['subtopics'].append(el_json)
                        c_json['items'].append(sc_json)
            response.append(c_json)
        print("suda habis run")
        

        return Response(response)

import json
import datetime
from core.helpers import convert_string_to_file


# CULPRIT
class SyncView(APIView):
    permission_classes = (AllowAny, )

    def post(self, request):
        print("Initiating SyncView Inspection")

        print("Post Body", request.data)

        ### REQUEST
        # Request Data
        data = request.data
        result1 = data['result1']
        result2 = data['result2']
        result_photos = data['photos']
        result_partners = data['partner']
        projectID = data['projectID']
        assessorName = data['assessorName']
        assessorId = data['assessorId']
        coordinate = data['coordinate']
        print(projectID)

        print("len1", len(result1))
        print("len2", len(result2))
        
        partners = ''
        for partner in json.loads(result_partners):
            partner_results = partner['result']
            partners += str(partner_results)

        ad = AssessmentData.objects.get(qaa__id=projectID)
        qaa = ad.qaa

        sync = SyncResult.objects.create(
            qaa=qaa,
            assessor=assessorName,
            coordinate=coordinate
        )
        
        # Clear the old data
        # element_results = ElementResult.objects.all().filter(qaa=qaa)
        # sample_results = SampleResult.objects.all().filter(qaa=qaa)
        # if element_results != None:
        #     element_results.delete()
        # if sample_results != None:
        #     sample_results.delete()

        # Result 1
        print("result1", result1)
        print("breakpoint1")
    
        erList = []
        for sub1 in json.loads(result1):
            id = sub1['id']
            id = id.replace(str(qaa.id)+'_+', '')
            id = id.replace('_thirdResult', '')
            id_array = id.split('+')

            results = sub1['result']
            erList = []
            for result in results:
                block = result['block']
                unit = result['unit']
                period = result['period']
                test_type = result['testType']
                selection_value = result['selectionValue']
                sample_id = result['sampleid']
                photo = result['photo']
                    
                sample_result = SampleResult.objects.create(
                    block=block,
                    unit=unit,
                    period=period,
                    test_type=test_type,
                    selection_value=selection_value,
                    sample_id=sample_id,
                    assessor_name=assessorName,
                    assessor_id=assessorId,
                    partners=partners,
                    qaa=qaa,
                    sync=sync,
                    sync_code=str(sync.id)
                )
                if photo != 'assets/add.png':
                    photo_data, photo_name = convert_string_to_file(photo, 'photo_1')
                    sample_result.photo_1.save(photo_name, photo_data)
                
                topics = result['topics']
                
                i = 0
                for topic in topics:
                    element_id = id_array[i]
                    element_name = topic['topic']
                    subtopics = topic['subtopics']
                    for subtopic in subtopics:
                        dg_name = subtopic['subtopic']
                        dg_result = subtopic['result']
                        total_compliance = 0
                        total_check = 0
                        for data in dg_result:
                            if data == "Yes":
                                total_compliance += 1
                            if data != 'NA':
                                total_check += 1

                        ## Pending, upload picture       
                        
                        er = ElementResult(
                             qaa=qaa,
                             sample_result=sample_result,
                             element_name=element_name,
                             element_code=element_id,
                             dg_name=dg_name,
                             test_type=test_type,
                             result=str(dg_result),
                             total_compliance=total_compliance,
                             total_check=total_check,
                             sync=sync,
                             sync_code=str(sync.id)
                        )

                        erList.append(er)
                    i += 1
                    
        er = ElementResult.objects.bulk_create(erList)


        # Result 2
        print("result2", result2)
        print("breakpoint2")
        
        erList = []
        for sub2 in json.loads(result2):
            id = sub2['id']
            id = id.replace(str(qaa.id)+'_', '')
            id = id.replace('_result', '')

            results = sub2['result']
            for result in results:
                if result != None:
                    sample_run = result['sampleRun']
                    remark = result['remark']
                    variables = result['variable']

                    sample_result = SampleResult.objects.create(
                        sample_run=sample_run,
                        remark=remark,
                        element_code=id,
                        assessor_name=assessorName,
                        assessor_id=assessorId,
                        partners=partners,
                        qaa=qaa,
                        sync=sync,
                        sync_code=str(sync.id)
                    )


                    for photo in json.loads(result_photos):
                        if result['pic'] == photo['id']:
                            pic_result = photo['result']
                            if pic_result[0] != 'assets/add.png':
                                photo_data, photo_name = convert_string_to_file(pic_result[0], 'photo_1')
                                sample_result.photo_1.save(photo_name, photo_data)
                            if pic_result[1] != 'assets/add.png':
                                photo_data, photo_name = convert_string_to_file(pic_result[1], 'photo_2')
                                sample_result.photo_2.save(photo_name, photo_data)
                            if pic_result[2] != 'assets/add.png':
                                photo_data, photo_name = convert_string_to_file(pic_result[2], 'photo_3')
                                sample_result.photo_3.save(photo_name, photo_data)
                            if pic_result[3] != 'assets/add.png':
                                photo_data, photo_name = convert_string_to_file(pic_result[3], 'photo_4')
                                sample_result.photo_4.save(photo_name, photo_data)
                            break
                    for variable in variables:
                        dg_name = variable['name']
                        dg_result = variable['result']
                        total_compliance = 0
                        total_check = 0
                        
                        for data in dg_result:
                            if data == "Yes":
                                total_compliance += 1
                            if data != 'NA':
                                total_check += 1
                        #ElementResult.objects.create (
                        #    qaa=qaa,
                        #    element_code=id,
                        #    dg_name=dg_name,
                        #    result=str(dg_result),
                        #    total_compliance=total_compliance,
                        #    total_check=total_check,
                        #    sample_result=sample_result,
                        #    sync=sync,
                        #    sync_code=str(sync.id)
                        #)
                        er = ElementResult(
                            qaa=qaa,
                            element_code=id,
                            dg_name=dg_name,
                            result=str(dg_result),
                            total_compliance=total_compliance,
                            total_check=total_check,
                            sample_result=sample_result,
                            sync=sync,
                            sync_code=str(sync.id)

                        )
                        erList.append(er)

        er = ElementResult.objects.bulk_create(erList)
        print('Synced')
        ### RESPONSE
        components = Component.objects.all().order_by('created_date')
        
        result_table = []
        label_table = []
        for component in components:

            sample_complete = 0

            sub_components = SubComponent.objects.all().filter(component=component).order_by('created_date')
            if component.type == 1:
                for sub_component in sub_components:
                    if sub_component.type == 3:
                        total_p = SampleResult.objects.all().filter(qaa=qaa,test_type="P",sync=sync).count()
                        total_s = SampleResult.objects.all().filter(qaa=qaa,test_type="S",sync=sync).count()
                        total_c = SampleResult.objects.all().filter(qaa=qaa,test_type="C",sync=sync).count()
                        result_table.append(total_p)
                        label_table.append('P')
                        result_table.append(total_s)
                        label_table.append('S')
                        result_table.append(total_c)
                        label_table.append('C')
                        sample_complete = sample_complete + total_p + total_s + total_c
                    elif sub_component.type == 2:
                        elements = Element.objects.all().filter(sub_component=sub_component).order_by('created_date')
                        for element in elements:
                            sr = SampleResult.objects.all().filter(
                                Q(element_code=element.id,qaa=qaa,sync=sync)|
                                Q(element_code=element.code_id,qaa=qaa,sync=sync)
                            )
                            total_e = len(sr)
                            label_table.append(element.name)
                            result_table.append(total_e)
                            sample_complete = sample_complete + total_e
                    else:
                        pass      
            else:
                for sub_component in sub_components:
                    elements = Element.objects.all().filter(sub_component=sub_component).order_by('created_date')
                    for element in elements:
                        sr = SampleResult.objects.all().filter(
                            Q(element_code=element.id,qaa=qaa,sync=sync)|
                            Q(element_code=element.code_id,qaa=qaa,sync=sync)
                        )
                        total_e = len(sr)
                        sample_complete = sample_complete + total_e
                label_table.append(component.name)
                result_table.append(sample_complete)

        print("sync process start")
        sync.result = str(result_table)
        sync.label = str(label_table)
        sync.sync_complete = True
        sync.save()

        response = sync_object(ad)
        print("response", response)

        return Response(response)

class OverviewView(APIView):
    permission_classes = (AllowAny, )

    def get(self, request, projectID):
        ad = AssessmentData.objects.get(qaa__id=projectID)
        qaa = ad.qaa
        response = sync_object(ad)
        return Response(response)

## Sync function for OverviewView and SyncView
def sync_object(ad):
    qaa = ad.qaa

    ### RESPONSE
    components = Component.objects.all().order_by('created_date')
    response = {}
    
    response['information'] = {
        'projectID': qaa.id,
        'projectCode': qaa.qaa_number,
        'projectName': qaa.pi.project_title,
        'phase': 'On-Going',
        'startDate': qaa.assessment_date
    }
    response['header'] = []
    response['body'] = []
    for component in components:

        subtopic_array = []
        subtopic_count = 0
        sample_complete = 0
        sample_total = ad.number_of_sample

        sub_components = SubComponent.objects.all().filter(component=component).order_by('created_date')
        if component.type == 1:
            for sub_component in sub_components:
                if sub_component.type == 3:
                    total_p = SampleResult.objects.all().filter(qaa=qaa,test_type="P").count()
                    total_s = SampleResult.objects.all().filter(qaa=qaa,test_type="S").count()
                    total_c = SampleResult.objects.all().filter(qaa=qaa,test_type="C").count()
                    subtopic_array.append('P')
                    subtopic_array.append('S')
                    subtopic_array.append('C')
                    sample_complete = sample_complete + total_p + total_s + total_c
                    subtopic_count += 3
                elif sub_component.type == 2:
                    elements = Element.objects.all().filter(sub_component=sub_component).order_by('created_date')
                    for element in elements:
                        sr = SampleResult.objects.all().filter(
                            Q(element_code=element.id,qaa=qaa)|
                            Q(element_code=element.code_id,qaa=qaa)
                        )
                        total_e = len(sr)
                        subtopic_array.append(element.name)
                        sample_complete = sample_complete + total_e
                        subtopic_count += 1
                else:
                    pass      

            response_header = {
                "topic": component.name,
                "type": component.type,
                "subtopictotal": subtopic_count,
                "subtopic": subtopic_array,
                "complete": sample_complete,
                "total": sample_total,

                # israa codes starts here

                "p": total_p,
                "s": total_s,
                "c": total_c,
                "total_external": sample_total - total_p - total_s - total_c,
            }
            response['header'].append(response_header)
        else:
            sample_total = 1
            for sub_component in sub_components:
                elements = Element.objects.all().filter(sub_component=sub_component).order_by('created_date')
                for element in elements:
                    sr = SampleResult.objects.all().filter(
                        Q(element_code=element.id,qaa=qaa)|
                        Q(element_code=element.code_id,qaa=qaa)
                    )
                    total_e = len(sr)
                    sample_complete = sample_complete + total_e
            response_header = {
                "topic": component.name,
                "type": component.type,
                "subtopictotal": subtopic_count,
                "subtopic": subtopic_array,
                "complete": sample_complete,
                "total": sample_total,
            }
            response['header'].append(response_header)

    sync_results = SyncResult.objects.all().filter(qaa=qaa).order_by('-created_date')
    for sync_result in sync_results:
        sync_result_sync_time = sync_result.created_date + datetime.timedelta(hours=8)
        sync_result_sync_time = sync_result_sync_time.strftime("%d/%m/%Y, %H:%M:%S")
        sync_result_job_status = sync_result_sync_time + "\n" + sync_result.assessor
        sync_result_body = {
            'jobStatus': sync_result_job_status,
            'syncID': str(sync_result.id),
            'syncTime':sync_result_sync_time,
            'resultTable':json.loads(sync_result.result)
        }
        response['body'].append(sync_result_body)

    return response


class CompleteView(APIView):
    def post(self, request):
        data = request.data
        coordinate = data['coordinate']
        name = data['name']
        nric = data['nric']
        company = data['company']
        position = data['position']
        contact_number = data['contactNumber']
        email = data['email']
        weather = data['weather']
        attendances = data['attendance'] #list
        project_id = data['projectID']
        dateSigned = data['dateSigned']
        signature = data['signature'] #base64

        print(project_id)
        print(nric)

        ad = AssessmentData.objects.get(qaa__id=project_id)
        qaa = ad.qaa

        try:
            assessor = Assessor.objects.get(user__icno=nric)
        except ObjectDoesNotExist:
            pass

        days = qaa.no_of_days - 1
        end_date = qaa.assessment_date + datetime.timedelta(days=days)

        wcf, created = WorkCompletionForm.objects.get_or_create(qaa=qaa)
        #wcf.assessor=assessor
        #wcf.assessor_number=assessor.assessor_no
        wcf.coordinate=coordinate
        wcf.weather=weather
        wcf.name=name
        wcf.icno=nric
        wcf.company=company
        wcf.position=position
        wcf.hp_no=contact_number
        wcf.email=email
        wcf.assessment_start_date=qaa.assessment_date
        wcf.assessment_end_date=end_date
        wcf.number_of_sample=ad.number_of_sample

        photo_data, photo_name = convert_string_to_file(signature, 'signature')
        wcf.signature.save(photo_name, photo_data)
        wcf.save()
        
        if attendances != 'undefined':
            for attendance in json.loads(attendances):
                att_name = attendance['name']
                if att_name != '':
                    att_position = attendance['position']
                    att_company = attendance['company']
                    att_signature = attendance['signature'] # base64
                    att_contact = attendance['contact']
                    
                    sa = SiteAttendance.objects.create(
                        qaa=qaa,
                        qaa_no=qaa.qaa_number,
                        name=att_name,
                        position=att_position,
                        hp_no=att_contact,
                        company=att_company
                    )
                    if att_signature != '':
                        photo_data, photo_name = convert_string_to_file(att_signature, 'signature')
                        sa.signature.save(photo_name, photo_data)
                    sa.save()

        response = {
            'projectId':project_id,
            'result':'true',
        }

        qaa.application_status = 'completed'
        qaa.save()

        assigneds = AssignedAssessor.objects.all().filter(ad=ad)
        for assigned in assigneds:
            assigned.complete = True
            assigned.save()

        return Response(response)

class GetAgreementView(APIView):
    def get(self, request, projectID):
        string_agreement = '<p>Dengan ini, saya selaku wakil pemohon mengesahkan bahawa kerja-kerja penilaian oleh Pegawai Penilai QLASSIC telah disiapkan sepenuhnya. Penilaian tersebut juga telah dijalankan sebagaimana ketetapan seperti berikut:</p>'
        string_agreement += '<ol>'
        string_agreement += '<li>Segala penemuan dari segi kepatuhan/ketidakpatuhan/tidak berkenaan telah dilengkapi dan direkodkan dalam borang penilaian sebagaimana keperluan Standard Industri Pembinaan (CIS7);dan</li>'
        string_agreement += '<li>Penilaian telah dijalankan ke atas setiap komponen dan elemen bangunan yang terdapat dan boleh dinilai dalam projek ini.</li>'
        string_agreement += '</ol>'
        string_agreement += '<p>Selain itu, saya juga faham bahawa persijilan QLASSIC termasuk laporan penilaian dan skor rasmi bagi projek ini akan dikeluarkan oleh CIDB melalui pihak yang telah dilantik</p>'
        
        response = {
            'projectId':projectID,
            'agreement':string_agreement
        }
        return Response(response)

class AppNoView(APIView):
    def get(self, request, projectID):
        qaa = QlassicAssessmentApplication.objects.get(id=projectID)
        response = {
            'projectId': projectID,
            'applicationNo': qaa.qaa_number
        }
        return Response(response)

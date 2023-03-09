from zeep import Client
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport
from zeep.settings import Settings
from django.contrib import messages
from django.conf import settings

from zeep.plugins import HistoryPlugin

from django.http import HttpResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

from decouple import config

from projects.models import Contractor, ProjectInfo
from assessments.models import QlassicAssessmentApplication

from api.helpers.crypto import encrypt_data_rsa, decrypt_data_rsa

import json
import requests
import xmltodict
import datetime

#quick patch -> use staging punya cims
# CIMS_WSDL = config('CIMS_WSDL', default='http://202.171.33.96/CIMSService/CIMSService.svc?wsdl')
CIMS_WSDL = config('CIMS_WSDL', default='http://cims.cidb.gov.my/CIMSService/CIMSService.svc?wsdl')
certificate_path = 'C:/nginx/ssl/qlassic_cidb_gov_my.pem'
if settings.CUSTOM_STG_MODE == 1: 
    certificate_path = 'C:/nginx/ssl/star_cidb_gov_my.pem'

def get_project(contractor_registration_number):
   
    check_applied_contractor(contractor_registration_number)
    contractors = Contractor.objects.all().filter(contractor_registration_number=contractor_registration_number)
    contractors.delete()
    cims_contractor, cims_projects, grade = request_contractor(contractor_registration_number)
    if cims_projects != None:
        for data in cims_projects:
            try:
                Contractor.objects.create(
                    name_of_contractor = cims_contractor.companyName,
                    contractor_registration_number = cims_contractor.ppkRegistrationNumber,
                    contractor_registration_grade = grade,
                    ssm_number = cims_contractor.ssmNo,
                    contract_value = data.Value,
                    project_title = data.Name,
                    project_status = data.Name,
                    project_location = data.Location,
                    project_reference_number = data.Id,
                    letter_of_award_date = data.LOADate,
                    start_date = data.StartDate,
                    dateline = data.EndDate,
                    client_name = data.ClientName,
                    registered_address = cims_contractor.registeredAddress,
                    registered_postcode = cims_contractor.registeredPostcode,
                    registered_city = cims_contractor.registeredTown,
                    registered_state = cims_contractor.registeredState,
                    correspondence_address = cims_contractor.correspondenceAddress,
                    correspondence_postcode = cims_contractor.correspondencePostcode,
                    correspondence_city = cims_contractor.correspondenceTown,
                    correspondence_state = cims_contractor.correspondenceState,
                )
                check_applied_contractor(contractor_registration_number)
                contractors = Contractor.objects.all().filter(contractor_registration_number=contractor_registration_number)
            except Exception as e:
                print("error", e)
                pass
    
    return contractors

def request_contractor(contractor_registration_number):
    wsdl = CIMS_WSDL
    print(wsdl)

    # session = Session()
    # session.auth = HTTPBasicAuth("RFID_INTEGRATION", "Rfid_1nt")

    # client = Client(wsdl, transport=Transport(session=session),
    #                 settings=Settings(strict=False, raw_response=True))
    
    session = Session()
    session.verify = False
    client = Client(
        wsdl, 
        transport=Transport(session=session),
        settings=Settings(strict=False)
    )

    request_data = {
        # 'EncryptedData': '195139',
        # 'EncryptedData': '1961018-SL009468',
        # 'EncryptedData': '0120020729-PH073265',
        'EncryptedData': (str(contractor_registration_number).encode("utf-8")),
    }

    contractor = client.service.GetContractorInfoNoEnc(**request_data)

    projects = None
    if contractor.projectList == None:
        projects = None
    else:
        projects = contractor.projectList.ProjectInfo
    # To get grade value
    grade = ''
    try: 
        specialization_list = contractor.specialization.SpecializationInfo
        for specialization in specialization_list:
            if specialization.Specialization.find('B04') != -1:
                grade = specialization.Grade
                break
    except Exception as e:
        print("cims error", e)
        pass

    return contractor, projects, grade

def test_request_contractor(request):
    wsdl = CIMS_WSDL

    # session = Session()
    # session.auth = HTTPBasicAuth("RFID_INTEGRATION", "Rfid_1nt")

    # client = Client(wsdl, transport=Transport(session=session),
    #                 settings=Settings(strict=False, raw_response=True))
    
    history = HistoryPlugin()
    try:
        session = Session()
        session.verify = False
        if settings.CUSTOM_DEV_MODE == 0:
            session.verify = certificate_path

        client = Client(wsdl,plugins=[history],transport=Transport(session=session))
    
        request_data = {
            # 'EncryptedData': '195139',
            'EncryptedData': '1961018-SL009468',
            # 'EncryptedData': '0120020729-PH073265',
        }

        response = client.service.GetContractorInfo(**request_data)
        
        return HttpResponse(str(response))
    except Exception:
        messages.warning(request, 'Error connecting with CIMS WSDL')
        return HttpResponse(str('Error connecting with CIMS WSDL'))
    

def verify_contractor(contractor_registration_number):
    wsdl = CIMS_WSDL
    print("the wsdl", wsdl)

    # session = Session()
    # session.auth = HTTPBasicAuth("RFID_INTEGRATION", "Rfid_1nt")

    # client = Client(wsdl, transport=Transport(session=session),
    #                 settings=Settings(strict=False, raw_response=True))
    
    history = HistoryPlugin()

    session = Session()
    # session.verify = False
    session.verify = certificate_path

    client = Client(
        wsdl, 
        transport=Transport(session=session),
        settings=Settings(strict=False)
    )

    request_data = {
        # 'EncryptedData': '195139',
        # 'EncryptedData': '1961018-SL009468',
        # 'EncryptedData': '0120020729-PH073265',
        'EncryptedData': (str(contractor_registration_number).encode("utf-8")),
    }

    try:
        # line ni error dekat production
        response = client.service.GetContractorInfoNoEnc(**request_data)
    except ValueError as e:
        print("verify_contractor_error", e)

    print(response)
    found = False
    message = ''
    if response.ssmNo != None:
        found = True
        
    else:
        print('not found contractor')
        found = False
        message = 'Record not found in CIMS System. Please correct your details to verify again.'

    return found, message

def check_applied_contractor(contractor_registration_number):
    contractors = Contractor.objects.all().filter(contractor_registration_number=contractor_registration_number)
    for contractor in contractors:
        qaa_found = QlassicAssessmentApplication.objects.all().filter(
            pi__contractor_cidb_registration_no=contractor.contractor_registration_number,
            pi__project_reference_number=contractor.project_reference_number
        ).order_by('-created_date')
        if len(qaa_found) > 0:
            qaa = qaa_found[0]
            if qaa.application_status == None:
                contractor.applied = False
            elif qaa.application_status == '':
                contractor.applied = False
            elif qaa.application_status == 'rejected':
                contractor.applied = False
            elif qaa.application_status == 'rejected_amendment':
                contractor.applied = False
            else:
                contractor.applied = True
        else:
            contractor.applied = False
        contractor.save()
    
    contractor_filtered = contractors.filter(applied=False)

    return 'filtered the contractor'

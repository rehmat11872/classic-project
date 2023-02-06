from zeep import Client
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport
from zeep.settings import Settings

from zeep.plugins import HistoryPlugin

from django.http import HttpResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder


from projects.models import Contractor

import json
import requests
import xmltodict
import datetime

CIMS_WSDL = config('CIMS_WSDL', default='http://202.171.33.96/CIMSService/CIMSService.svc?wsdl')

def get_contractor(ssm_number):
    contractors = Contractor.objects.all().filter(ssm_number=ssm_number)
    if len(contractors) < 1:
        cims_contractors, grade = request_contractor(ssm_number)
        for data in cims_contractors:
            Contractor.objects.create(
                name_of_contractor = data.companyName,
                contractor_registration_number = data.ppkRegistrationNumber,
                contractor_registration_grade = grade,
                ssm_number = data.ssmNo,
                contract_value = data.Value,
                project_title = data.Name,
                project_location = data.Location,
                project_reference_number = data.Id,
                letter_of_award_date = data.LOADate,
                start_date = data.StartDate,
                dateline = data.EndDate,
                client_name = data.ClientName,
                registered_address = data.registeredAddress,
                registered_postcode = data.registeredPostcode,
                registered_city = data.registeredTown,
                registered_state = data.registeredState,
                correspondence_address = data.correspondenceAddress,
                correspondence_postcode = data.correspondencePostcode,
                correspondence_city = data.correspondenceTown,
                correspondence_state = data.correspondenceState,
            )
        contractors = Contractor.objects.all().filter(ssm_number=ssm_number)
    return contractors

def request_contractor(ssm_number):
    # payload = {
    #     "token": "tLh-KkVgm8yUgA30ulJNFA",
    #     "data": {
    #     "name": "nameFirst",
    #     "email": "internetEmail",
    #     "phone": "phoneHome",
    #     "_repeat": 300
    #     }
    # };

    # r = requests.post("http://167.71.199.123:8080/getEmployee.php", json = payload)
    # return json.loads(r.content);

    wsdl = CIMS_WSDL
    wsdl = CIMS_WSDL

    # session = Session()
    # session.auth = HTTPBasicAuth("RFID_INTEGRATION", "Rfid_1nt")

    # client = Client(wsdl, transport=Transport(session=session),
    #                 settings=Settings(strict=False, raw_response=True))
    
    history = HistoryPlugin()
    client = Client(wsdl,plugins=[history])
    request_data = {
        # 'EncryptedData': '195139',
        # 'EncryptedData': '1961018-SL009468',
        # 'EncryptedData': '0120020729-PH073265',
        'EncryptedData': str(ssm_number),
    }

    response = client.service.GetContractorInfo(**request_data)
    
    # To get grade value
    specialization_list = response.specialization.SpecializationInfo
    grade = ''
    for specialization in specialization_list:
        # print(specialization.Specialization.find('B04'))
        if specialization.Specialization.find('B04') != -1:
            grade = specialization.Grade
            break
    # print(grade)

    
    # print(history.last_sent)
    # print(history.last_received)
    # serialized_obj = json.dumps(list(response), cls=DjangoJSONEncoder)
    # print(type(response))
    # response_xml = response.projectList.ProjectInfo
    # for pl in response_xml:
    #     print(pl)

    # Contractor.objects.create(
    #     name_of_contractor = response.companyName
    #     contractor_registration_number = response.ppkRegistrationNumber
    #     contractor_registration_grade = 
    #     project_type
    #     contract_type
    #     levy_number
    #     ssm_number = response.ssmNo
    #     contract_value = response.Value
    #     project_title = response.Name
    #     project_location = response.Location
    #     project_reference_number = response.Id

    #     letter_of_award_date = response.LOADate
    #     start_date = response.StartDate
    #     dateline = response.EndDate
        
    #     client_name = response.ClientName
    #     registered_address = response.registeredAddress
    #     registered_postcode = response.registeredPostcode
    #     registered_city = response.registeredTown
    #     registered_state = response.registeredState
    #     
    #     correspondence_address = response.correspondenceAddress
    #     correspondence_postcode = response.correspondencePostcode
    #     correspondence_city = response.correspondenceTown
    #     correspondence_state = response.correspondenceState
    # )

    # return response.projectList.ProjectInfo
    # return HttpResponse(str(response.projectList.ProjectInfo))
    
    # return HttpResponse(str(response))
    return response, grade


    # print(response_xml)
    # middleware_response_json = json.loads(
    #     json.dumps(xmltodict.parse(response_xml)))
    # return HttpResponse(middleware_response_json)
    # return middleware_response_json
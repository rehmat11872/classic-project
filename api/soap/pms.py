from zeep import Client
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport
from zeep.settings import Settings

from zeep.plugins import HistoryPlugin

from django.http import HttpResponse
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder

from decouple import config

from projects.models import Contractor, ProjectInfo

import json
import requests
import xmltodict
import datetime

PMS_WSDL = config('PMS_WSDL', default='http://202.171.33.96/Financeservice/?wsdl')

def test_create_transaction():
    wsdl = PMS_WSDL

    # session = Session()
    # session.auth = HTTPBasicAuth("RFID_INTEGRATION", "Rfid_1nt")

    # client = Client(wsdl, transport=Transport(session=session),
    #                 settings=Settings(strict=False, raw_response=True))
    
    history = HistoryPlugin()
    client = Client(wsdl,plugins=[history])
    request_data = {
        # 'EncryptedData': 'test',
    }

    contractor = client.service.CreateTransaction(**request_data)
    projects = None
    if contractor.projectList == None:
        projects = None
    else:
        projects = contractor.projectList.ProjectInfo
    # To get grade value
    specialization_list = contractor.specialization.SpecializationInfo
    grade = ''
    for specialization in specialization_list:
        if specialization.Specialization.find('B04') != -1:
            grade = specialization.Grade
            break

    return contractor, projects, grade
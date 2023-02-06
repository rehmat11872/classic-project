from zeep import Client
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep.transports import Transport
from zeep.settings import Settings

from zeep.plugins import HistoryPlugin

from zeep.xsd import SkipValue

from django.http import HttpResponse
from django.conf import settings

import json
import requests
import xmltodict
import datetime

# Staging URL
create_transaction_wsdl = "http://202.171.33.96/Financeservice/?wsdl"
payment_gateway_url = "https://cimsdev.cidb.gov.my/pmscart/Payment/MakePayment"
get_receipt_url = "http://202.171.33.96:8080/ReceiptEnquiry/?code="
transaction_history_url = "https://cimsdev.cidb.gov.my/pmscart/?customerDebtorId="
## FULL URL PATTERN: https://cimsdev.cidb.gov.my/pmscart/?customerDebtorId=USR210007&ClientReturnURL=https://cimsdev.cidb.gov.my/securepay/test.aspx#

# payment_gateway_url = "http://202.171.33.96:8085/Payment/MakePayment"
# payment_gateway_url = "http://202.171.33.96/securepay/Listener.aspx"

# Production URL
# create_transaction_wsdl = "http://202.171.33.96/Financeservice/?wsdl"
# payment_gateway_url = "https://www.icims.cidb.gov.my:8085/Payment/MakePayment"
if settings.CUSTOM_PROD_MODE == 1:
    create_transaction_wsdl = "http://www.icims.cidb.gov.my/Financeservice/?wsdl"
    get_receipt_url = "http://www.icims.cidb.gov.my:8080/ReceiptEnquiry/?code="
    payment_gateway_url = "https://www.icims.cidb.gov.my:8085/Payment/MakePayment"
    transaction_history_url = "https://www.icims.cidb.gov.my/pmscart/?customerDebtorId="


# Get KodHasil By Code
def get_kodhasil(code):

    wsdl = create_transaction_wsdl

    history = HistoryPlugin()
    client = Client(wsdl,plugins=[history])
    request_data = {
        'code':code,
    }
    print(str(request_data))

    response = client.service.GetKodHasilbyCode(**request_data)
    # print(history.last_sent)
    # print(history.last_received)
    # response_xml = response.content
    print(response)
    # print(type(response_xml))
    return response

# Get KodHasil By Code
def get_transaction_detail(code):

    wsdl = create_transaction_wsdl

    history = HistoryPlugin()
    client = Client(wsdl,plugins=[history])
    request_data = {
        'code':code,
    }
    print(str(request_data))

    response = client.service.GetKodHasilbyCode(**request_data)
    # print(history.last_sent)
    # print(history.last_received)
    # response_xml = response.content
    # print(type(response_xml))
    return response

# Create Transaction
def create_transaction(request, quantity, kod_hasil, description, ref_id, user):
    ## Notes

    # Clear unnecessary symbols
    ref_id = ref_id.replace(' ','')
    ref_id = ref_id.replace('(','')
    ref_id = ref_id.replace(')','')
    
    # KOD HASIL : QLC - assessment, QLC-PUP - training
    # kh_response = get_transaction_detail(kod_hasil)
    # print(kh_response)

    # unit_amount = kh_response[0].unitPrice
    # discount_amount = kh_response[0].discountAmount
    # # unit_amount_with_tax = unit_amount + ( unit_amount * kh_response[0].taxPercentage)
    # tax_amount_per_unit = unit_amount * kh_response[0].taxPercentage
    
    
    # total_tax =  tax_amount_per_unit * quantity
    # # total_amount = unit_amount_with_tax * quantity

    # total_unit_amount = unit_amount * quantity
    # amount = total_unit_amount

    response = create_transaction_process(user, quantity, False, 0, ref_id, description, kod_hasil)

    # If amount is changed, cancel the old proforma
    # if response.ErrorMessage == 'Discrepancy in Amount':
    #     cancel_proforma(response.Code)
    #     response = create_transaction_process(user, quantity, False, 0, ref_id, description, kod_hasil)
    
    return response
from decimal import Decimal

# Create Training Transaction
def create_training_transaction(request, amount, kod_hasil, description, ref_id, user):
    ## Notes

    # Clear unnecessary symbols
    ref_id = ref_id.replace(' ','')
    ref_id = ref_id.replace('(','')
    ref_id = ref_id.replace(')','')

    # KOD HASIL : QLC - assessment, QLC-PUP - training
    # kh_response = get_transaction_detail(kod_hasil)

    # print(kh_response)

    # discount_amount = kh_response[0].discountAmount
    # tax_amount_per_unit = Decimal(amount) * Decimal(kh_response[0].taxPercentage)
    
    # total_tax =  tax_amount_per_unit 


    response = create_transaction_process(user, 1, True, amount, ref_id, description, kod_hasil)
    
    # If amount is changed, cancel the old proforma
    # if response.ErrorMessage == 'Discrepancy in Amount':
    #     cancel_proforma(response.Code)
    #     response = create_transaction_process(user, 1, True, amount, ref_id, description, kod_hasil)
    
    return response

def create_transaction_process(user, quantity, custom_amount, amount, ref_id, description, kod_hasil):
    prefix = ''
    if settings.CUSTOM_DEV_MODE == 1:

        prefix = 'DP' + datetime.datetime.now().strftime("%y%m")
        prefix = 'DP' + datetime.datetime.now().strftime("%y%m")
    elif settings.CUSTOM_STG_MODE == 1:
        prefix = 'SP' + datetime.datetime.now().strftime("%y%m")
        prefix = 'SP' + datetime.datetime.now().strftime("%y%m")
    else:
        prefix = 'P' + datetime.datetime.now().strftime("%y%m")
        prefix = 'P' + datetime.datetime.now().strftime("%y%m")

    wsdl = create_transaction_wsdl

    history = HistoryPlugin()
    client = Client(wsdl,plugins=[history])
    now_date = datetime.datetime.now()
    due_date = now_date + datetime.timedelta(days=14)
    request_data = {}
    if custom_amount == False:
        request_data = {
            'obj': {
                'Id':'1',
                'SubType':'QLASSIC',
                'Category':'PROFORMA INVOICE',
                'SubCategory':'Third Party System - QLASSIC Portal',
                'SourceType':'Third Party System - QLASSIC Portal',
                'CustomerId': user.code_id,
                'PostingDate': SkipValue,
                'CreatedDate': str(now_date.strftime("%Y-%m-%dT%H:%M:%S")),
                'ReceiptDate': str(now_date.strftime("%Y-%m-%dT%H:%M:%S")),
                'TransactionDate': str(now_date.strftime("%Y-%m-%dT%H:%M:%S")),
                'DueDate': str(due_date.strftime("%Y-%m-%dT%H:%M:%S")),
                'Description': prefix+ref_id,
                'Amount': SkipValue,
                'AmountDec': SkipValue,
                'DiscountAmount': SkipValue,
                'Tax': SkipValue,
                'TaxDec': SkipValue,
                'UniqueReference': prefix+ref_id,
                'SMISRefId': prefix+ref_id,
                'CreatedBy': user.name,
                'CustomerName': user.name,
                'address': user.address1,
                'address1': user.address2,
                'address2': '',
                'city': user.city,
                'state': user.state,
                'zipCode': user.postcode,
                'BranchCode': 'HQ',
                'ModuleCode': 'B4',
                'ComId': SkipValue,
                'PaymentTerm': SkipValue,
                'isWriteOff': SkipValue,
                'isRefund': SkipValue,
                'isDoubtfulDebts': SkipValue,
                'isCancel': SkipValue,
                'Items' : {
                    'TransactionDetail': [{
                        'Id': SkipValue,
                        'DiscountPer': SkipValue,
                        'KodHasil': kod_hasil,
                        'UnitPrice': SkipValue,
                        'UnitPriceDec': SkipValue,
                        'Qty': quantity,
                        'QtyAmount': SkipValue,
                        'QtyAmountDec': SkipValue,
                        'TaxCode': SkipValue,
                        'TaxPerAmount': SkipValue,
                        'TaxPerAmountDec': SkipValue,
                        'TaxAmount': SkipValue,
                        'TaxAmountDec': SkipValue,
                        'Amount': SkipValue,
                        'AmountDec': SkipValue,
                        'DiscountAmount': SkipValue,
                        'CMISRefId': prefix+ref_id,
                        'Description': prefix+ref_id,
                    }]
                }
            }
        }
    else:
        request_data = {
            'obj': {
                'Id':'1',
                'SubType':'QLASSIC',
                'Category':'PROFORMA INVOICE',
                'SubCategory':'Third Party System - QLASSIC Portal',
                'SourceType':'Third Party System - QLASSIC Portal',
                'CustomerId': user.code_id,
                'PostingDate': SkipValue,
                'CreatedDate': str(now_date.strftime("%Y-%m-%dT%H:%M:%S")),
                'ReceiptDate': str(now_date.strftime("%Y-%m-%dT%H:%M:%S")),
                'TransactionDate': str(now_date.strftime("%Y-%m-%dT%H:%M:%S")),
                'DueDate': str(due_date.strftime("%Y-%m-%dT%H:%M:%S")),
                'Description': prefix+ref_id,
                'Amount': amount,
                'AmountDec': SkipValue,
                'DiscountAmount': SkipValue,
                'Tax': SkipValue,
                'TaxDec': SkipValue,
                'UniqueReference': prefix+ref_id,
                'SMISRefId': prefix+ref_id,
                'CreatedBy': user.name,
                'CustomerName': user.name,
                'address': user.address1,
                'address1': user.address2,
                'address2': '',
                'city': user.city,
                'state': user.state,
                'zipCode': user.postcode,
                'BranchCode': 'HQ',
                'ModuleCode': 'B4',
                'ComId': SkipValue,
                'PaymentTerm': SkipValue,
                'isWriteOff': SkipValue,
                'isRefund': SkipValue,
                'isDoubtfulDebts': SkipValue,
                'isCancel': SkipValue,
                'Items' : {
                    'TransactionDetail': [{
                        'Id': SkipValue,
                        'DiscountPer': SkipValue,
                        'KodHasil': kod_hasil,
                        'UnitPrice': amount,
                        'UnitPriceDec': SkipValue,
                        'Qty': quantity,
                        'QtyAmount': SkipValue,
                        'QtyAmountDec': SkipValue,
                        'TaxCode': SkipValue,
                        'TaxPerAmount': SkipValue,
                        'TaxPerAmountDec': SkipValue,
                        'TaxAmount': SkipValue,
                        'TaxAmountDec': SkipValue,
                        'Amount': SkipValue,
                        'AmountDec': SkipValue,
                        'DiscountAmount': SkipValue,
                        'CMISRefId': prefix+ref_id,
                        'Description': prefix+ref_id,
                    }]
                }
            }
        }
    print(str(request_data))

    response = client.service.CreateTransaction(**request_data)
    print(response)
    return response

def cancel_proforma(code):
    wsdl = create_transaction_wsdl

    history = HistoryPlugin()
    client = Client(wsdl,plugins=[history])
    request_data = {
        'proforma':code,
        'cancelBy':'Admin',
        'cancelRemark':'Proforma Expired'
    }

    response = client.service.CancelProforma(**request_data)
    # print(history.last_sent)
    # print(history.last_received)
    # response_xml = response.content
    # print(type(response_xml))
    print(response)
    return response
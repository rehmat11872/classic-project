from assessments.models import SampleResult, SyncResult
import shutil
import os

from app.helpers.docx2pdf import TEMPLATE_TEMP_PATH
def job_remove_temp():
    print("Cron: Remove Temp files")
    if os.path.exists(TEMPLATE_TEMP_PATH):
        shutil.rmtree(TEMPLATE_TEMP_PATH) 
        print('JOB: Clear up tmp folder')

# Models
from billings.models import Payment
from projects.models import Contractor, VerifiedContractor

# API
from api.soap.create_transaction import cancel_proforma
from api.soap.get_contractor import get_project

import datetime
from django.utils.timezone import localtime, now
from django.db.models import Q

def job_cancel_proforma():
    print("Cron: Cancel Proforma")
    due_date = localtime(now()) - datetime.timedelta(days=14)
    expired_payments = Payment.objects.all().filter(
        Q(created_date__lt=due_date,payment_status="0",proforma_cancelled=False)|
        Q(created_date__lt=due_date,payment_status="-1",proforma_cancelled=False)
    )
    for payment in expired_payments:
        status = cancel_proforma(payment.order_id)
        if status.TransactionResult == "PASS":
            payment.proforma_cancelled=True
            payment.save()

def job_remove_failed_sync():
    print("Cron: Delete Failed Sync Result")
    sync_results = SyncResult.objects.all().filter(sync_complete=False)
    if len(sync_results) > 0:
        sync_results.delete()

def job_update_contractor_info():
    print("Cron: Update Contractor Results")
    verified_contractors = VerifiedContractor.objects.all().distinct('contractor_registration_number')
    current_contractors = Contractor.objects.all()
    if len(current_contractors) > 0:
        current_contractors.delete()

    count = 0 # check if there is new data
    for ver in verified_contractors:
        ver.contractor_registration_number
        updated = get_project(ver.contractor_registration_number)
        count += len(updated)

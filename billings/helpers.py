# Helpers
from .models import Payment
from datetime import datetime

def get_claim_category_name(slug):
    if slug == 'mileage':
        return 'Mileage'

    if slug == 'fi':
        return 'FI'

    if slug == 'public_transport':
        return 'Public Transport'

    if slug == 'accommodation':
        return 'Accommodation'

    if slug == 'others':
        return 'Others'

def payment_response_process(request):
    status = request.POST['Status']
    if status != None:
        order_id = request.POST['OrderID']
        status_desc = request.POST['StatusDesc']

        payment, created = Payment.objects.get_or_create(order_id=order_id)
        payment.payment_status = int(status)
        payment.status_description = status_desc
        
        # If payment successful
        if status == '1':
            transaction_date = request.POST['TransactionDate']
            transaction_id = request.POST['TransactionID']
            payment_method_desc = request.POST['PaymentMethodDesc']
            payment_method = request.POST['PaymentMethod']
            auth_code = request.POST['AuthCode']
            receipt_no = request.POST['ReceiptNo']
        
            payment.payment_method = payment_method
            payment.payment_method_description = payment_method_desc
            payment.payment_date = datetime.strptime(transaction_date, "%d/%m/%Y %H:%M:%S")
            payment.transaction_id = transaction_id
            payment.auth_code = auth_code
            payment.receipt_number = receipt_no
        payment.save()

        return payment
    else:
        return None

from api.soap.create_transaction import transaction_history_url

def get_payment_history_url(request):
    return transaction_history_url + request.user.code_id
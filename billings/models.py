from assessments.models import QlassicAssessmentApplication
from django.db import models
import uuid

# Models
from users.models import CustomUser
from trainings.models import Training
# from trainings.models import RegistrationTraining, TrainingCertificate
# from assessments.models import QlassicAssessmentApplication

# Helpers
from core.helpers import PathAndRename, STATE_CHOICES
import datetime

# Signals
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True,blank=True, max_length=50)

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    rt = models.ForeignKey('trainings.RegistrationTraining', on_delete=models.CASCADE, null=True, blank=True)
    ra = models.ForeignKey('trainings.RoleApplication', on_delete=models.CASCADE, null=True, blank=True)
    qaa = models.ForeignKey('assessments.QlassicAssessmentApplication', on_delete=models.CASCADE, null=True, blank=True)
    
    customer_name = models.CharField(null=True, blank=True, max_length=255)
    customer_email = models.CharField(null=True, blank=True, max_length=255)
    currency = models.CharField(null=True, blank=True, max_length=255)
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_amount = models.DecimalField(null=True, blank=True, max_digits=8, decimal_places=2, verbose_name="Amount (RM)")
    order_id = models.CharField(null=True, blank=True, max_length=255)
    transaction_id = models.CharField(null=True, blank=True, max_length=255)
    
    PAYMENT_METHOD = [
        # To follow SRS
        ('FPX','Online Banking'),
        ('CCX','Credit/ Debit card'),
    ]
    payment_method = models.CharField(
        null=True,
        blank=True,
        choices=PAYMENT_METHOD,
        max_length=50
    )
    payment_method_description = models.CharField(null=True, blank=True, max_length=255)
    auth_code = models.CharField(null=True, blank=True, max_length=255)
    receipt_number = models.CharField(null=True, blank=True, max_length=255)

    PAYMENT_STATUS = [
        # To follow SRS
        ("2",'Pending Authorization (Applicable for B2B model)'),
        ("1",'Successful'),
        ("0",'Fail'),
        ("-1",'Pending'),
    ]
    payment_status = models.CharField(
        default="-1",
        choices=PAYMENT_STATUS,
        max_length=15
    )
    proforma_cancelled = models.BooleanField(null=True,default=False)
    status_description = models.CharField(null=True, blank=True, max_length=255)

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50, blank=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50, blank=True)
    
    def save(self,*args, **kwargs):
        if not self.code_id:
            prefix = 'PY{}'.format(datetime.datetime.now().strftime('%y'))
            prev_instances = self.__class__.objects.filter(code_id__contains=prefix)
            if prev_instances.exists():
                last_instance_id = prev_instances.first().code_id.replace(prefix,'')
                self.code_id = prefix+'{0:04d}'.format(int(last_instance_id)+1)
            else:
                self.code_id = prefix+'{0:04d}'.format(1)
            
        super(Payment, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return str(self.order_id)

class ClaimApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True, max_length=50)
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True, blank=True)
    training = models.ForeignKey(Training, on_delete=models.CASCADE, null=True, blank=True)

    CLAIM_CATEGORY = [
        # To follow SRS
        ('mileage','Mileage'),
        ('fi','FI'),
        ('public_transport','Public Transport'),
        ('accommodation','Accommodation'),
        ('others','Others'),
    ]
    claim_category = models.CharField(
        null=True,
        choices=CLAIM_CATEGORY,
        max_length=50
    )

    CLAIM_STATUS = [
        # To follow SRS
        ('pending','Pending'),
        ('rejected','Rejected'),
        ('verified','Verified'),
        ('approved','Approved'),
    ]
    claim_status = models.CharField(
        default='pending',
        null=True,
        choices=CLAIM_STATUS,
        max_length=50
    )

    OTHER_TYPE = [
        # To follow SRS
        ('mileage','Mileage'),
        ('fi','FI'),
        ('public_transport','Public Transport'),
        ('accommodation','Accommodation'),
        ('others','Others'),
    ]
    other_type = models.CharField(
        null=True,
        choices=OTHER_TYPE,
        max_length=50
    )

    TRANSPORT_TYPE = [
        # To follow SRS
        ('airplane','Airplane'),
        ('train','Train'),
        ('car','Car'),
        ('bus','Bus'),
    ]
    transport_type = models.CharField(
        null=True,
        choices=TRANSPORT_TYPE,
        max_length=50
    )

    ACCOMMODATION_TYPE = [
        # To follow SRS
        ('hotel','Hotel'),
        ('lojing','Lojing'),
    ]
    accommodation_type = models.CharField(
        null=True,
        choices=ACCOMMODATION_TYPE,
        max_length=50
    )

    location_from = models.CharField(null=True, blank=True, max_length=255)
    location_to = models.CharField(null=True, blank=True, max_length=255)
    state_from = models.CharField(choices=STATE_CHOICES, null=True, max_length=50)
    state_to = models.CharField(choices=STATE_CHOICES, null=True, max_length=50)
    time_from = models.TimeField(null=True)
    time_to = models.TimeField(null=True)
    date_from = models.DateField(null=True)
    date_to = models.DateField(null=True)

    # Transportation Detail
    transport_model = models.CharField(null=True, max_length=50, verbose_name='Transport Model')
    transport_cc = models.FloatField(null=True, verbose_name='CC')
    transport_registration_number = models.CharField(null=True, max_length=50, verbose_name='Transport Registration Number')

    notes = models.CharField(null=True, max_length=255)
    mileage = models.FloatField(null=True)
    receipt_number = models.CharField(null=True, max_length=255)

    # Zone
    zone = models.CharField(null=True, blank=True, max_length=255)
    
    # Amount 
    total_receipt_amount = models.DecimalField(null=True, max_digits=20, decimal_places=2, verbose_name="Amount")

    date_of_transaction = models.DateField(null=True, verbose_name='Date of Transaction')
    attachments = models.FileField(null=True, max_length=255, upload_to=PathAndRename('billings'))

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)
   
    def __str__(self):
        return str(self.id)

@receiver(post_save, sender=ClaimApplication)
def create_claim_application(sender, instance, created, **kwargs):
    if created:
        code = ''
        count = ClaimApplication.objects.all().exclude(code_id=None).count()
        if count > 0:
            top = ClaimApplication.objects.exclude(code_id=None).order_by('-created_date')[0]
            if top == None:
                code = datetime.datetime.now().strftime('%y') + str(1).zfill(5)
            else:
                created_date = top.created_date
                if created_date.strftime('%y') != datetime.datetime.now().strftime('%y'):
                    code = datetime.datetime.now().strftime('%y') + str(1).zfill(5)
                else:
                    if top.code_id == None or top.code_id == '':
                        code = datetime.datetime.now().strftime('%y') + str(1).zfill(5)
                    else:
                        top_serial = int(top.code_id[2:])
                        code = datetime.datetime.now().strftime('%y') + str(top_serial+1).zfill(5)
        else:
            code = datetime.datetime.now().strftime('%y') + str(1).zfill(5)
        instance.code_id = code
        instance.save()

class OnlineBanking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    
    account_description = models.CharField(null=True, max_length=255)
    
    ACCOUNT_TYPE = [
        # To follow SRS
        ('saving_account','Saving Account'),
    ]
    account_type = models.CharField(
        null=True,
        choices=ACCOUNT_TYPE,
        max_length=50
    )

    ACCOUNT_BANK = [
        # To follow SRS
        ('cimbclicks','CIMB Clicks'),
        ('maybank2u','Maybank2u'),
        ('affinbank','Affin Bank'),
        ('bsn','Bank Simpanan Nasional'),
    ]
    account_bank = models.CharField(
        null=True,
        choices=ACCOUNT_BANK,
        max_length=50
    )

    account_number = models.CharField(null=True, max_length=15)

    def __str__(self):
        return self.id

class CreditDebitCard(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    card_no = models.CharField(null=True, max_length=50, verbose_name="Credit/ Debit card number")
    name_on_card = models.CharField(null=True, max_length=255)
    
    expired_date = models.DateField(null=True, verbose_name="Expired date (month/year)")

    cvc = models.IntegerField(null=True)

    def __str__(self):
        return self.id

class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ob = models.ForeignKey(OnlineBanking, on_delete=models.CASCADE, null=True)
    cdc = models.ForeignKey(CreditDebitCard, on_delete=models.CASCADE, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True)
    payment_description = models.CharField(null=True, max_length=255)
    
    RECEIPT_TYPE = [
        # To follow SRS
        ('receipt','Receipt'),
        ('invoice','Invoice'),
    ]
    receipt_type = models.CharField(
        null=True,
        choices=RECEIPT_TYPE,
        max_length=50
    )
    receipt_description = models.CharField(null=True, max_length=255)

    def __str__(self):
        return self.id
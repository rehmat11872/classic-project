from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
import datetime

from .managers import CustomUserManager
import uuid

# Helpers
from core.helpers import PathAndRename, STATE_CHOICES

# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), max_length=100, unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True,blank=True, max_length=50)

    icno = models.CharField(null=True, max_length=12, verbose_name='Identity Card Number (without \'-\')')
    name = models.CharField(null=True, max_length=100)

    GENDER = [
        # To follow SRS
        ('MALE', 'MALE'),
        ('FEMALE', 'FEMALE'), 
    ]

    gender = models.CharField(
        null=True,
        max_length=10,
        choices=GENDER,
    )  

    MARITAL_STATUS = [
        # To follow SRS
        ('SINGLE','SINGLE'),
        ('MARRIED','MARRIED'),
        ('OTHERS','OTHERS'), 
    ]

    marital_status = models.CharField(
        null=True,
        max_length=10,
        choices=MARITAL_STATUS,
    )      

    greencard_no = models.CharField(null=True, blank=True, max_length=30, verbose_name='Green card number')
    greencard_exp_date = models.DateField(null=True, blank=True, verbose_name='Green card\'s expired date')

    organization = models.TextField(null=True, max_length=50)
    position = models.CharField(null=True, max_length=50)
    
    ROLE_CHOICES = [
        # To follow SRS
        ('superadmin','Super Admin'),
        ('staff','Staff'),
        ('contractor','Contractor'),
        # ('assessor','Assessor'),
        ('none','None'),
        ('trainee','Trainee'),
        # ('applicant','Applicant'),
        ('casc_reviewer','CASC Reviewer'),
        ('casc_verifier','CASC Verifier'),
        ('casc_approver','CASC Approver'),
        ('cidb_reviewer','CIDB Reviewer'),
        ('cidb_verifier','CIDB Verifier'),
        ('cidb_approver','CIDB Approver'),
    ]
    
    role = models.CharField(
        null=True,
        choices=ROLE_CHOICES,
        max_length=50
    )

    # Assessor
    # qia_eligible = models.BooleanField(default=False, null=True)
    PAYMENT_MODE = [
        # To follow SRS
        ('on','On'),
        ('off','Off'),
    ]
    qia_payment_mode = models.CharField(
        null=True,
        choices=PAYMENT_MODE,
        max_length=5
    )
    
    QIA_STATUS = [
        # To follow SRS
        ('','Not Eligible'),
        ('need_review','Need Review'),
        ('need_payment','Need Payment'),
        ('approved','Approved'),
    ]
    qia_status = models.CharField(
        null=True,
        blank=True,
        default='',
        choices=QIA_STATUS,
        max_length=50
    )

    PAYMENT_STATUS = [
        # To follow SRS
        ("2",'Pending Authorization (Applicable for B2B model)'),
        ("1",'Successful'),
        ("0",'Fail'),
        ("-1",'Pending'),
        ("-2",'-'),
    ]
    qia_payment_status = models.CharField(
        null=True,
        default="-2",
        choices=PAYMENT_STATUS,
        max_length=15
    )

    # Transportation Detail
    transport_model = models.CharField(null=True, blank=True, max_length=50, verbose_name='Transport Model')
    transport_cc = models.FloatField(null=True, blank=True, verbose_name='CC')
    transport_registration_number = models.CharField(null=True, blank=True, max_length=50, verbose_name='Transport Registration Number')

    # Home Address
    address1 = models.CharField(null=True, max_length=100)
    address2 = models.CharField(null=True, max_length=100)
    postcode = models.CharField(null=True, max_length=10, verbose_name='Postal code')
    city = models.CharField(null=True, max_length=50)
    state = models.CharField(choices=STATE_CHOICES, null=True, max_length=50)    
    
    # Office Address
    # office_address1 = models.CharField(null=True, max_length=100)
    # office_address2 = models.CharField(null=True, max_length=100)
    # office_postcode = models.IntegerField(null=True, verbose_name='Postal code')
    # office_city = models.CharField(null=True, max_length=20)
    # office_state = models.CharField(choices=STATE_CHOICES, null=True, max_length=20)    

    # Phone
    office_no = models.CharField(null=True, max_length=15, verbose_name='Office phone number')
    hp_no = models.CharField(null=True, max_length=15, verbose_name='Mobile number')
    fax_no = models.CharField(null=True, max_length=15, verbose_name='Fax number')
    
    picture = models.FileField(null=True, blank=True, upload_to=PathAndRename('images'), verbose_name='Profile picture')
    
    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)
    
    def save(self,*args, **kwargs):
        if not self.code_id:
            prefix = 'USR{}'.format(datetime.datetime.now().strftime('%y'))
            prev_instances = self.__class__.objects.filter(code_id__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().code_id[-3:]
                self.code_id = prefix+'{0:04d}'.format(int(last_instance_id)+1)
            else:
                self.code_id = prefix+'{0:04d}'.format(1)
        if self.role == '' or self.role == None:
            self.role = 'none'  
        super(CustomUser, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.email
    
    def is_assessor(self):
        assessor = Assessor.objects.all().filter(user=self)
        if len(assessor) > 0:
            return True
        else:
            return False

    def is_trainer(self):
        assessor = Trainer.objects.all().filter(user=self)
        if len(assessor) > 0:
            return True
        else:
            return False

# @receiver(post_save, sender=SubComponent)
# def signal_sub_component(sender, instance, created, **kwargs):
#     if instance.
    # if created:
    #     instance.created_by = 
    # else:
    #     instance.profile.referral_code = 'NXU' + str(instance.profile.id) 
    # instance.save()

class AcademicQualification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    
    year = models.IntegerField(null=True, verbose_name="Graduation year")
    institution = models.CharField(null=True, max_length=50, verbose_name="Name of institution")
    
    QUALIFICATION = [
        # To follow SRS
        ('spm', 'SPM'),
        ('diploma', 'Diploma'), 
        ('degree', 'Degree'), 
        ('master', 'Master'), 
        ('phd', 'PHD'), 
    ]
    qualification = models.CharField(
        null=True,
        max_length=50,
        choices=QUALIFICATION,
    )  

    program = models.CharField(null=True, max_length=50, verbose_name="Academic program")

    # Date
    created_by = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name

class WorkExperience(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    
    year_from = models.IntegerField(null=True, verbose_name="Year start")
    year_to = models.IntegerField(null=True, verbose_name="Year end")
    position = models.CharField(null=True, max_length=50)
    company = models.CharField(null=True, max_length=50)

    # Date
    created_by = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.name

class Assessor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, unique=True, on_delete=models.CASCADE, null=True)
    qia_id = models.CharField(null=True,blank=True, max_length=50)
    qca_id = models.CharField(null=True,blank=True, max_length=50)
    assessor_no = models.CharField(null=True,blank=True, max_length=50, verbose_name='Assessor number')
    
    qia_certificate_file = models.FileField(null=True, blank=True, upload_to=PathAndRename('interview_letter'), verbose_name='QIA Certificate File')
    qia_certificate_qr_file = models.ImageField(null=True, blank=True, upload_to=PathAndRename('interview_letter/qr/'), verbose_name='QIA Certificate QR File')

    ASSESSOR_TYPE = [
        # To follow SRS
        ('QIA', 'QLASSIC Industry Assessor'),
        ('QCA', 'QLASSIC CIDB Assessor'),
    ]
    assessor_type = models.CharField(
        default='QIA',
        null=True,
        max_length=50,
        choices=ASSESSOR_TYPE,
    )  

    # Date
    created_by = models.CharField(null=True,blank=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True,blank=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self,*args, **kwargs):
        if self.assessor_type == 'QCA':
            if not self.qca_id:
                prefix = 'CQA '
                postfix = '/{}'.format(datetime.datetime.now().strftime('%y'))
                prev_instances = self.__class__.objects.filter(qca_id__contains=postfix).order_by('-created_date')
                if prev_instances.exists():
                    last_instance_id = prev_instances.first().qca_id[-4:-3]
                    self.qca_id = prefix+'{0:03d}'.format(int(last_instance_id)+1)+postfix
                else:
                    self.qca_id = prefix+'{0:03d}'.format(1)+postfix
                self.assessor_no = self.qca_id
            super(Assessor, self).save(*args, **kwargs)
        if self.assessor_type == 'QIA':
            if not self.qia_id:
                prefix = 'IQA '
                postfix = '/{}'.format(datetime.datetime.now().strftime('%y'))
                prev_instances = self.__class__.objects.filter(qia_id__contains=postfix).order_by('-created_date')
                if prev_instances.exists():
                    last_instance_id = prev_instances.first().qia_id[-4:-3]
                    self.qia_id = prefix+'{0:03d}'.format(int(last_instance_id)+1)+postfix
                else:
                    self.qia_id = prefix+'{0:03d}'.format(1)+postfix
                self.assessor_no = self.qia_id
            super(Assessor, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.user.email

class Trainer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    trainer_no = models.CharField(null=True, blank=True, max_length=50, verbose_name='Trainer number')

    # Date
    created_by = models.CharField(null=True, blank=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, blank=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self,*args, **kwargs):
        if not self.trainer_no:
            prefix = 'QT{}'.format(datetime.datetime.now().strftime('%y'))
            prev_instances = self.__class__.objects.filter(trainer_no__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().trainer_no[-3:]
                self.trainer_no = prefix+'{0:04d}'.format(int(last_instance_id)+1)
            else:
                self.trainer_no = prefix+'{0:04d}'.format(1)
            
        super(Trainer, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.user.email

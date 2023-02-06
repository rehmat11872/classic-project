from django.db import models
# from billings.models import Payment
from django.db.models import Q

# Models
from users.models import Trainer, Assessor, CustomUser

# Helpers
from core.helpers import STATE_CHOICES, PathAndRename
import uuid, datetime

# Signals
from django.db.models.signals import post_save
from django.dispatch import receiver

ORGANIZATION_TYPE_CHOICES = [
    # To follow SRS
    ('Contractor', 'Contractor'),
    ('Developer', 'Developer'),
    ('Consultant', 'Consultant'),
    ('Individual ', 'Individual'),
]

# Create your models here.
class RoleApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, null=True, blank=True)
    assessor = models.ForeignKey(Assessor, on_delete=models.CASCADE, null=True, blank=True)
    
    application_number = models.CharField(max_length=255, null=True, blank=True)
    
    APPLICATION_STATUS = [
        # To follow SRS
        ('pending', 'Pending'),
        ('interview_invitation', 'Interview Invitation'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
    ]
    
    application_status = models.CharField(
        default='',
        null=True,
        max_length=255,
        choices=APPLICATION_STATUS,
    )

    APPLICATION_TYPE = [
        # To follow SRS
        ('qca', 'QLASSIC CIDB Assessor'),
        ('trainer', 'Trainer'),
    ]
    
    application_type = models.CharField(
        default='',
        null=True,
        max_length=255,
        choices=APPLICATION_TYPE,
    )

    interview_date = models.DateField(null=True,blank=True)
    interview_time_from = models.TimeField(null=True,blank=True)
    interview_time_to = models.TimeField(null=True,blank=True)
    interview_location = models.TextField(null=True,blank=True, max_length=2000)
    interview_sent = models.BooleanField(null=True, default=False)

    accreditation_duration_month = models.IntegerField(null=True,blank=True)
    accreditation_duration_year = models.IntegerField(null=True,blank=True)
    
    interview_letter_file = models.FileField(null=True, blank=True, upload_to=PathAndRename('interview_letter'), verbose_name='Interview Letter')
    reject_letter_file = models.FileField(null=True, blank=True, upload_to=PathAndRename('interview_letter'), verbose_name='Rejection Letter')
    accreditation_letter_file = models.FileField(null=True, blank=True, upload_to=PathAndRename('interview_letter'), verbose_name='Accreditation Letter')
    accreditation_certificate_file = models.FileField(null=True, blank=True, upload_to=PathAndRename('interview_letter'), verbose_name='Accreditation Certificate')
    certificate_qr_file = models.ImageField(null=True, blank=True, upload_to=PathAndRename('interview_letter/qr/'), verbose_name='QR File')
    
    reviewed_by = models.CharField(null=True, max_length=255)
    approved_by = models.CharField(null=True, max_length=255)
    remarks = models.TextField(null=True, blank=True, max_length=255)
    
    # Date
    created_by = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self,*args, **kwargs):
        if not self.application_number:
            prefix = 'QRA'
            prev_instances = self.__class__.objects.filter(application_number__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().application_number.replace(prefix,'')
                self.application_number = prefix+'{0:06d}'.format(int(last_instance_id)+1)
            else:
                self.application_number = prefix+'{0:06d}'.format(1)
            
        super(RoleApplication, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return '%s' % (self.user)

class JoinedTraining(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    
    year = models.IntegerField(null=True, verbose_name='Year join the training')
    course = models.CharField(null=True, max_length=50)
    place = models.CharField(null=True, max_length=50)

    # Date
    created_by = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user

class TrainingType(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    name = models.CharField(null=True, max_length=30)
    required_for_assessor = models.BooleanField(default=False, null=True, verbose_name="Required For Becoming Assessor?")
    template_file = models.FileField(null=True, upload_to=PathAndRename('templates'))

    CERT_TYPE = [
        # To follow SRS
        ('attendance', 'Attendance'),
        ('pass', 'Pass'),
    ]
    
    cert_type = models.CharField(
        null=True,
        max_length=30,
        choices=CERT_TYPE,
        verbose_name='Certificate Type',
    )

    # Date
    created_by = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Training(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True,blank=True, max_length=50)
    trainer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    
    # TRAINING_TYPE = [
    #     # To follow SRS
    #     ('module1', 'Module 1'),
    #     ('module2', 'Module 2'), 
    #     ('exam', 'Exam'), 
    #     ('practical', 'Practical'), 
    #     ('test', 'Test'), 
    # ]
    training_name = models.CharField(null=True, max_length=255, verbose_name="Training Name")
    training_type = models.ForeignKey(TrainingType, on_delete=models.CASCADE, null=True)
    from_date = models.DateField(null=True, verbose_name='Start Date')
    to_date = models.DateField(null=True, verbose_name='End Date')
    from_time = models.TimeField(null=True, verbose_name='Start Time')
    to_time = models.TimeField(null=True, verbose_name='End Time')
    size = models.IntegerField(null=True, verbose_name='Available Seat')
    passing_mark = models.DecimalField(null=True, default=0, max_digits=6, decimal_places=2, verbose_name="Passing Mark")
    ccd_point = models.DecimalField(null=True, max_digits=6, decimal_places=2, verbose_name="CCD Point")
    fee = models.DecimalField(null=True, max_digits=8, decimal_places=2, verbose_name="Fees (RM)")

    reviewed_by = models.CharField(null=True, max_length=50)
    reviewed_date = models.DateTimeField(null=True)
    review_status = models.TextField(null=True, blank=True, max_length=255, verbose_name="Remarks 1 - by CASC Reviewer")

    REVIEW_STATUS = [
        # To follow SRS
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    review_status = models.CharField(
        default='pending',
        null=True,
        max_length=40,
        choices=REVIEW_STATUS,
        verbose_name='Status',
    )

    ATTENDANCE_REVIEW_STATUS = [
        # To follow SRS
        ('pending', 'Pending'),
        ('need_approval', 'Submit For Approval'),
        ('approved', 'Approved'),
    ]
    
    attendance_review_status = models.CharField(
        default='pending',
        null=True,
        max_length=40,
        choices=ATTENDANCE_REVIEW_STATUS,
        verbose_name='Attendance Review Status',
    )

    CERT_TYPE = [
        # To follow SRS
        ('attendance', 'Attendance'),
        ('pass', 'Pass'),
    ]
    
    cert_type = models.CharField(
        null=True,
        max_length=30,
        choices=CERT_TYPE,
        verbose_name='Certificate Type',
    )

    attendance_sheet_file = models.FileField(null=True, blank=True, upload_to=PathAndRename('attendance_sheet'), verbose_name='Attendance Sheet')
    
    address1 = models.CharField(null=True, max_length=255)
    address2 = models.CharField(null=True, max_length=255)
    postcode = models.CharField(null=True, max_length=10, verbose_name='Postal Code')
    city = models.CharField(null=True, max_length=255)
    state = models.CharField(choices=STATE_CHOICES, null=True, max_length=255)
    
    # coach = models.CharField(null=True, max_length=255)
    
    publish = models.BooleanField(default=False, verbose_name="Published?")

    # Date
    created_by = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.training_name

    def number_of_days(self):
        days = self.to_date - self.from_date
        return days.days + 1

    def current_pax(self):
        registered = RegistrationTraining.objects.all().filter(training=self)
        current_seat = registered.filter(
            Q(status="accepted")|
            Q(status="need_payment")
        ).count()
        
        return current_seat
    
    def is_available(self):

        # Check Expired date
        now = datetime.date.today()
        if now >= self.from_date:
            return False
        
        # Check if full
        registered = RegistrationTraining.objects.all().filter(training=self)
        current_seat = registered.filter(
            Q(status="accepted")|
            Q(status="need_payment")
        ).count()

        available_seat = self.size - current_seat
        available = True
        if available_seat < 1:
            available = False

        return available

    def save(self,*args, **kwargs):
        if not self.code_id:
            prefix = 'TR{}'.format(datetime.datetime.now().strftime('%y'))
            prev_instances = self.__class__.objects.filter(code_id__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().code_id.replace(prefix,'')
                self.code_id = prefix+'{0:04d}'.format(int(last_instance_id)+1)
            else:
                self.code_id = prefix+'{0:04d}'.format(1)
            
        super(Training, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']

class Coach(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    training = models.ForeignKey(Training, on_delete=models.CASCADE, null=True)
    email = models.EmailField(max_length=30)
    name = models.CharField(null=True, max_length=100)
    hp_no = models.CharField(null=True, max_length=15, verbose_name='Contact Number')

    def __str__(self):
        return '%s' % (self.name)

class RegistrationTraining(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True,blank=True, max_length=50)

    training = models.ForeignKey(Training, on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    # REGISTRATION_TYPE = [
    #     # To follow SRS
    #     ('individual', 'Individual'),
    #     ('group', 'Group'),
    # ]

    STATUS = [
        # To follow SRS
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('need_payment', 'Need Payment'),
    ]
    
    status = models.CharField(
        default='pending',
        null=True,
        max_length=40,
        choices=STATUS,
        verbose_name='Status',
    )
    
    # registration_type = models.CharField(
    #     null=True,
    #     max_length=255,
    #     choices=REGISTRATION_TYPE,
    # )
    
    participant_name = models.CharField(null=True, max_length=200, verbose_name="Participant's name")
    participant_icno = models.CharField(null=True, max_length=12, verbose_name="Participant's IC number (without '-')")
    participant_email = models.CharField(null=True, max_length=100, verbose_name="Participant's email")
    participant_hpno = models.CharField(null=True, max_length=15, verbose_name="Participant's phone number")
    participant_designation = models.CharField(null=True, max_length=200, verbose_name="Participant's designation")
    participant_organization = models.CharField(null=True, max_length=200, verbose_name="Participant's organization")
    participant_organization_type = models.CharField(
        null=True,
        default=True,
        max_length=50,
        choices=ORGANIZATION_TYPE_CHOICES,
    )
    
    reviewed_by = models.CharField(null=True, blank=True, max_length=255)
    remarks = models.TextField(null=True, blank=True, max_length=255, verbose_name="Remarks")

    PAYMENT_MODE = [
        # To follow SRS
        ('on', 'On'),
        ('off', 'Off'),
    ]
    payment_mode = models.CharField(
        null=True,
        default='off',
        max_length=5,
        choices=PAYMENT_MODE,
    )

    PAYMENT_STATUS = [
        # To follow SRS
        ("2",'Pending Authorization (Applicable for B2B model)'),
        ("1",'Successful'),
        ("0",'Fail'),
        ("-1",'Pending'),
        ("-2",'-'),
    ]
    payment_status = models.CharField(
        null=True,
        default="-2",
        choices=PAYMENT_STATUS,
        max_length=15
    )

    # Attendance
    ATTENDANCE_FULL = [
        # To follow SRS
        (True, 'FULL'),
        (False, 'NOT FULL'),
    ]
    attendance_full = models.BooleanField(
        null=True, 
        blank=True,
        choices=ATTENDANCE_FULL,
    )
    
    PASS_STATUS = [
        # To follow SRS
        (True, 'PASS'),
        (False, 'FAIL'),
    ]
    pass_status = models.BooleanField(
        null=True, 
        blank=True,
        choices=PASS_STATUS,
    )

    marks = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2)

    amount = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name="Amount (RM)")
    paid = models.BooleanField(default=False)

    certificate_file = models.FileField(null=True, blank=True, upload_to=PathAndRename('certificates'), verbose_name='Certificate')
    # payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True)

    # Date
    created_by = models.CharField(null=True, blank=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, blank=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

    def save(self,*args, **kwargs):
        if not self.code_id:
            prefix = 'RT'
            prev_instances = self.__class__.objects.filter(code_id__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().code_id.replace(prefix,'')
                self.code_id = prefix+'{0:06d}'.format(int(last_instance_id)+1)
            else:
                self.code_id = prefix+'{0:06d}'.format(1)
            
        super(RegistrationTraining, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return '%s - %s' % (self.user, self.training)

# class AttendanceMarks(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     # training = models.ForeignKey(Training, on_delete=models.CASCADE, null=True)
#     rt = models.ForeignKey(RegistrationTraining, on_delete=models.CASCADE, null=True)
    
#     participant_name = models.CharField(null=True, max_length=255, verbose_name="Participant's name")

#     ATTENDANCE_FULL = [
#         # To follow SRS
#         ('yes', 'Yes'),
#         ('no', 'No'),
#     ]

#     attendance_full = models.CharField(
#         null=True,
#         max_length=10,
#         choices=ATTENDANCE_FULL,
#     )

#     marks = models.FloatField(null=True)

#     # Date
#     created_by = models.CharField(null=True, max_length=50)
#     created_date = models.DateTimeField(auto_now_add=True)
#     modified_by = models.CharField(null=True, max_length=50)
#     modified_date = models.DateTimeField(auto_now=True)

class TrainingCertificate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    training = models.ForeignKey(Training, on_delete=models.CASCADE, null=True)
    
    TRAINING_TYPE = [
        # To follow SRS
        ('module1', 'Module 1'),
        ('module2', 'Module 2'),
        ('exam_practical_test', 'Exam Practical Test'),
    ]
    
    training_type = models.CharField(
        null=True,
        max_length=255,
        choices=TRAINING_TYPE,
    )
    
    rt = models.ForeignKey(RegistrationTraining, on_delete=models.CASCADE, null=True)
    
    participant_name = models.CharField(null=True, max_length=255, verbose_name="Participant's name")

    ATTENDANCE_FULL = [
        # To follow SRS
        ('yes', 'Yes'),
        ('no', 'No'),
    ]

    attendance_full = models.CharField(
        null=True,
        max_length=10,
        choices=ATTENDANCE_FULL,
    )

    marks = models.FloatField(null=True)

    CERTIFICATE_DESCRIPTION = [
        # To follow SRS
        ('attendance', 'Attendance'),
        ('marks', 'Marks'),
    ]

    certificate_description = models.CharField(
        null=True,
        max_length=10,
        choices=CERTIFICATE_DESCRIPTION,
    )

    fees = models.CharField(null=True, max_length=4)
    
    reviewed_by = models.CharField(null=True, max_length=255)
    reviewed_date = models.DateField(null=True)
    
    PAYMENT_STATUS = [
        # To follow SRS
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    ]

    payment_status = models.CharField(
        null=True,
        max_length=10,
        choices=PAYMENT_STATUS,
    )

    # Date
    created_by = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

class Feedback(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True, max_length=50)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    training = models.ForeignKey(Training, on_delete=models.CASCADE, null=True)

    description_1 = models.TextField(null=True, blank=True, max_length=3000)
    description_2 = models.TextField(null=True, blank=True, max_length=3000)
    
    warning = models.TextField(null=True, blank=True, max_length=3000)
    warning_delivered = models.BooleanField(null=True, default=False)
    warning_delivered_date = models.DateTimeField(null=True, blank=True)
    reviewer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, related_name='reviewer')

    # Date
    created_by = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)

@receiver(post_save, sender=Feedback)
def create_feedback(sender, instance, created, **kwargs):
    if created:
        code = ''
        count = Feedback.objects.all().exclude(code_id=None).count()
        if count > 0:
            top = Feedback.objects.exclude(code_id=None).order_by('-created_date')[0]
            if top == None:
                code = "CF" + str(1).zfill(5)
            else:
                if top.code_id == None or top.code_id == '':
                    code = "CF" + str(1).zfill(5)
                else:
                    top_serial = int(top.code_id[2:])
                    code = "CF" + str(top_serial+1).zfill(5)
        else:
            code = "CF" + str(1).zfill(5)
        instance.code_id = code
        instance.save()

from django.db import models
import uuid

from django.db.models.fields import IntegerField

# Models
from trainings.models import JoinedTraining, RoleApplication
from users.models import CustomUser, Assessor
from projects.models import ProjectInfo
# from projects.models import ProjectInfo

# Helper
from core.helpers import (
    PathAndRename, 
    STATE_CHOICES, 
    file_size_validator,
)

# Signals
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class QlassicAssessmentApplication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    qaa_number = models.CharField(null=True, max_length=50, verbose_name="QLASSIC Assessment Application Number")
    pi = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE, null=True)
    # sd = models.ForeignKey(SupportingDocuments, on_delete=models.CASCADE, null=True)
    # contractor = models.ForeignKey('projects.Contractor', on_delete=models.CASCADE, null=True)

    applicant_name = models.CharField(null=True, max_length=255)
    
    ROLE_CHOICES = [
        # To follow SRS
        ('superadmin','Super Admin'),
        ('contractor','Contractor'),
        ('assessor','Assessor'),
        ('trainer','Trainer'),
        ('trainee','Trainee'),
        ('applicant','Applicant'),
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
    
    organization = models.TextField(null=True, max_length=255)
    designation = models.CharField(null=True, blank=True, max_length=255)
    address1 = models.CharField(null=True, max_length=255, verbose_name="Address 1")
    address2 = models.CharField(null=True, max_length=255, verbose_name="Address 2")
    postcode = models.CharField(null=True, max_length=10, verbose_name='Postal code')
    city = models.CharField(null=True, max_length=50)
    state = models.CharField(choices=STATE_CHOICES, null=True, max_length=50)    

    hp_no = models.CharField(null=True, max_length=15, verbose_name='Contact number')
    fax_no = models.CharField(null=True, max_length=15, verbose_name='Fax number')
    email = models.CharField(null=True, max_length=255)
    
    CONTRACT_TYPE = [
        # To follow SRS
        ('lump_sum','Lump Sum'),
        ('provisional_quantity','Provisional Quantity'),
        ('lum_sump_and_quantity','Lump Sum and Quantity'),
    ]

    contract_type = models.CharField(
        null=True,
        choices=CONTRACT_TYPE,
        max_length=50
    )

    BUILDING_TYPE = [
        # To follow SRS
        ('A','A - Landed Housing'),
        ('B','B - Stratified Housing'),
        ('C','C - Public/ Commercial/ Industrial Building (Without centralized cooling system)'),
        ('D','D - Public/ Commercial/ Industrial Building (With centralized cooling system)'),
    ]
    building_type = models.CharField(
        null=True,
        choices=BUILDING_TYPE,
        max_length=50
    )
    
    project_declaration_number = models.CharField(null=True, blank=True, max_length=50)
    
    APPLICATION_STATUS = [
        # To follow SRS
        ('pending','Pending'),
        ('reviewed','Reviewed'),
        ('verified','Verified'),
        ('rejected','Rejected'),
        ('rejected_amendment','Rejected (With Amendment)'),
        ('need_payment','Need Payment'),
        ('assessor_assign','Assessor Assigned'),
        ('confirm','Confirm'),
        ('in_progress','In-Progress'),
        ('completed','Completed'),
        ('approved','Approved'),
    ]
    # add default value
    application_status = models.CharField(
        null=True,
        blank=True,
        choices=APPLICATION_STATUS,
        max_length=50
    )

    proposed_date = models.DateField(null=True, verbose_name='Proposed Date for Assessment')
    assessment_date = models.DateField(null=True, verbose_name="Assessment Date")

    no_of_days = models.IntegerField(null=True, verbose_name="Number of Days")

    NO_OF_ASSESSOR = [
        # To follow SRS
        (2,'2'),
        (4,'4'),
        (6,'6'),
        (8,'8'),
        (10,'10'),
    ]
    no_of_assessor = models.IntegerField(
        null=True,
        choices=NO_OF_ASSESSOR,
        verbose_name="Number of assessor",
    )

    no_of_blocks = models.IntegerField(null=True, verbose_name="Number of Block/Zone/Assessment")

    PAYMENT_MODE = [
        # To follow SRS
        ('on','On'),
        ('off','Off'),
    ]
    payment_mode = models.CharField(
        null=True,
        choices=PAYMENT_MODE,
        max_length=5
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

    qlassic_score = models.FloatField(null=True,blank=True, verbose_name='QLASSIC Score')

    # Reporting
    DOC_STATUS = [
        # To follow SRS
        ("pending",'Pending'),
        ("generated",'Report Generated'),
        ("casc_approved",'CASC Approved'),
        ("reviewed",'Reviewed'),
        ("verified",'Verified'),
        ("approved",'Approved'),
        ("submit",'Delivered to Applicant'),
    ]
    doc_qlassic_score_letter_status = models.CharField(null=True,default='pending',choices=DOC_STATUS,max_length=20)
    doc_qlassic_report_status = models.CharField(null=True,default='pending',choices=DOC_STATUS,max_length=20)
    doc_qlassic_certificate_status = models.CharField(null=True,default='pending',choices=DOC_STATUS,max_length=20)
    qlassic_score_letter_qr_file = models.ImageField(null=True, blank=True, upload_to=PathAndRename('assessment/qr/'), verbose_name='QLASSIC Score QR File')
    qlassic_report_qr_file = models.ImageField(null=True, blank=True, upload_to=PathAndRename('assessment/qr/'), verbose_name='QLASSIC Report QR File')
    qlassic_certificate_qr_file = models.ImageField(null=True, blank=True, upload_to=PathAndRename('assessment/qr/'), verbose_name='QLASSIC Cert QR File')

    # QLASSIC SCORE
    ccd_point = models.FloatField(null=True, default=20, verbose_name="CCD Point")
    qlassic_score = models.FloatField(null=True, blank=True, verbose_name="QLASSIC score")
    casc_qlassic_score = models.FloatField(null=True, blank=True, verbose_name="QLASSIC score from CASC Approver (Leave blank for actual score)")

    reviewed_by = models.CharField(null=True,blank=True, max_length=50)
    reviewed_date = models.DateTimeField(null=True,blank=True)
    remarks1 = models.TextField(null=True, blank=True, max_length=255, verbose_name="Remarks 1 - by CASC Reviewer")
    verified_by = models.CharField(null=True,blank=True, max_length=50)
    verified_date = models.DateTimeField(null=True,blank=True)
    remarks2 = models.TextField(null=True, blank=True, max_length=255, verbose_name="Remarks 2 - by CASC Verifier")
    # approved_by = models.CharField(null=True, max_length=50)
    # approved_date = models.DateTimeField(null=True)
    # remarks3 = models.TextField(null=True, blank=True, max_length=255)

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True,blank=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True,blank=True, max_length=50)
   
    def __str__(self):
        return "%s" % (self.qaa_number)
    
    def get_amount(self):
        multiply = self.no_of_blocks
        if multiply == None:
            return 1000.00
        else:
            return 1000.00 * multiply

class Component(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True,blank=True, max_length=50)

    name = models.CharField(null=True, max_length=255)
    TYPE_CHOICE = [
        (1,'Type 1'),
        (2,'Type 2')
    ]
    type = models.IntegerField(
        null=True,
        choices=TYPE_CHOICE,
        default=1
    )

    # weightage = models.DecimalField(null=True, max_digits=8, decimal_places=3, verbose_name="Weightage")
    weightage_a = models.DecimalField(null=True, max_digits=8, decimal_places=5, verbose_name="Weightage A")
    weightage_b = models.DecimalField(null=True, max_digits=8, decimal_places=5, verbose_name="Weightage B")
    weightage_c = models.DecimalField(null=True, max_digits=8, decimal_places=5, verbose_name="Weightage C")
    weightage_d = models.DecimalField(null=True, max_digits=8, decimal_places=5, verbose_name="Weightage D")

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    class Meta:
        ordering = ['-created_date']

    def save(self,*args, **kwargs):
        if not self.code_id:
            prefix = 'CO'
            prev_instances = self.__class__.objects.filter(code_id__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().code_id.replace(prefix,'')
                self.code_id = prefix+'{0:03d}'.format(int(last_instance_id)+1)
            else:
                self.code_id = prefix+'{0:03d}'.format(1)
            
        super(Component, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.name)

class SubComponent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    code_id = models.CharField(null=True,blank=True, max_length=50)

    name = models.CharField(null=True, max_length=255)
    component = models.ForeignKey(Component, on_delete=models.CASCADE, null=True)
    
    TYPE_CHOICE = [
        (0,'No Type'),
        (2,'Type 2'),
        (3,'Type 3'),
        # (4,'Type 4 (Unused)'),
        # (4,'Without Element (eg. Roof)')
    ]
    type = models.IntegerField(
        null=True,
        choices=TYPE_CHOICE,
        default=3
    )

    # weightage = models.DecimalField(null=True, max_digits=8, decimal_places=3, verbose_name="Weightage (%)")

    NO_OF_CHECK = [
        # To follow SRS
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
        (6,'6'),
        (7,'7'),
        (8,'8'),
        (9,'9'),
    ]
    no_of_check = models.IntegerField(
        null=True,
        choices=NO_OF_CHECK,
        verbose_name='Number of Check',
        default=1
    )

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    def __str__(self):
        return '%s' % (self.name)

    class Meta:
        ordering = ['-created_date']

    def save(self,*args, **kwargs):
        if not self.code_id:
            prefix = 'SC'
            prev_instances = self.__class__.objects.filter(code_id__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().code_id.replace(prefix,'')
                self.code_id = prefix+'{0:03d}'.format(int(last_instance_id)+1)
            else:
                self.code_id = prefix+'{0:03d}'.format(1)
            
        super(SubComponent, self).save(*args, **kwargs)


    def get_total_weightage(self):
        elements = Element.objects.all().filter(sub_component=self)
        total_weightage = 0
        for element in elements:
            if element.category_weightage == False:
                if element.weightage != None:
                    total_weightage += element.weightage   
        return total_weightage

class Element(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True,blank=True, max_length=50)

    sub_component = models.ForeignKey(SubComponent, on_delete=models.CASCADE, null=True)
    name = models.CharField(null=True, max_length=255)

    NO_OF_CHECK = [
        # To follow SRS
        (1,'1'),
        (2,'2'),
        (3,'3'),
        (4,'4'),
        (5,'5'),
        (6,'6'),
        (7,'7'),
        (8,'8'),
        (9,'9'),
    ]
    no_of_check = models.IntegerField(
        null=True,
        choices=NO_OF_CHECK,
        verbose_name='Number of Check',
        default=1
    )
    CATEGORY_WEIGHTAGE = [
        # To follow SRS
        (True,'Yes'),
        (False,'No (Default)'),
    ]
    category_weightage = models.BooleanField(null=True, choices=CATEGORY_WEIGHTAGE, default=False, verbose_name="Use As Category Weightage")
    weightage = models.DecimalField(null=True, blank=True, default=0, max_digits=8, decimal_places=3, verbose_name="Weightage")
    weightage_a = models.DecimalField(null=True, blank=True, default=0, max_digits=8, decimal_places=3, verbose_name="Weightage A")
    weightage_b = models.DecimalField(null=True, blank=True, default=0, max_digits=8, decimal_places=3, verbose_name="Weightage B")
    weightage_c = models.DecimalField(null=True, blank=True, default=0, max_digits=8, decimal_places=3, verbose_name="Weightage C")
    weightage_d = models.DecimalField(null=True, blank=True, default=0, max_digits=8, decimal_places=3, verbose_name="Weightage D")

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    class Meta:
        ordering = ['-created_date']

    def save(self,*args, **kwargs):
        if not self.code_id:
            prefix = 'EL'
            prev_instances = self.__class__.objects.filter(code_id__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().code_id.replace(prefix,'')
                self.code_id = prefix+'{0:03d}'.format(int(last_instance_id)+1)
            else:
                self.code_id = prefix+'{0:03d}'.format(1)
            
        super(Element, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.name)

    def get_no_of_defect_group(self):
        return DefectGroup.objects.all().filter(element=self).count()

class DefectGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True,blank=True, max_length=50)
    
    element = models.ForeignKey(Element, on_delete=models.CASCADE, null=True, blank=True)
    sub_component = models.ForeignKey(SubComponent, on_delete=models.CASCADE, null=True, blank=True)
    
    name = models.CharField(null=True, max_length=255)
    
    # NO_OF_CHECK = [
    #     # To follow SRS
    #     (1,'1'),
    #     (2,'2'),
    #     (3,'3'),
    #     (4,'4'),
    #     (5,'5'),
    # ]
    # no_of_check = models.IntegerField(
    #     null=True,
    #     choices=NO_OF_CHECK,
    #     verbose_name='Number of Check',
    #     default=1
    # )
    
    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    class Meta:
        ordering = ['-created_date']

    def save(self,*args, **kwargs):
        if not self.code_id:
            prefix = 'DG'
            prev_instances = self.__class__.objects.filter(code_id__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().code_id.replace(prefix,'')
                print(prev_instances.first().code_id)
                print(last_instance_id)
                print('{0:03d}'.format(int(last_instance_id)+1))
                self.code_id = prefix+'{0:03d}'.format(int(last_instance_id)+1)
            else:
                self.code_id = prefix+'{0:03d}'.format(1)
            
        super(DefectGroup, self).save(*args, **kwargs)

    def __str__(self):
        return '%s' % (self.name)

class AssessmentData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True, blank=True)
    assessor = models.ForeignKey(Assessor, on_delete=models.CASCADE, null=True, blank=True)
    
    # sub_component = models.ForeignKey(SubComponent, on_delete=models.CASCADE, null=True, blank=True)
    # dg = models.ForeignKey(DefectGroup, on_delete=models.CASCADE, null=True, blank=True)
    
    block = models.IntegerField(null=True, blank=True, verbose_name="Block's name")
    unit = models.IntegerField(null=True, blank=True, verbose_name="Unit number")
    time = models.TimeField(null=True, blank=True, verbose_name="Time taken to complete data for one sample")
    count_sampling_done = models.IntegerField(null=True, blank=True, verbose_name="Number of sampling done")
    count_principle = models.IntegerField(null=True, blank=True, verbose_name="Number of principles samples")
    count_services = models.IntegerField(null=True, blank=True, verbose_name="Number of services samples")
    count_circulation = models.IntegerField(null=True, blank=True, verbose_name="Number of circulation samples")
    
    number_of_sample = models.IntegerField(null=True, blank=True)
    ptotal = models.IntegerField(null=True, blank=True)
    stotal = models.IntegerField(null=True, blank=True)
    ctotal = models.IntegerField(null=True, blank=True)
    
    architectural_work = models.FloatField(null=True, blank=True)
    floor_finishes = models.FloatField(null=True, blank=True)
    internal_wall = models.FloatField(null=True, blank=True)
    ceiling = models.FloatField(null=True, blank=True)
    door = models.FloatField(null=True, blank=True)
    window = models.FloatField(null=True, blank=True)
    internal_fixtures = models.FloatField(null=True, blank=True)
    roof = models.FloatField(null=True, blank=True)
    external_wall = models.FloatField(null=True, blank=True)
    apron_perimeter_drain = models.FloatField(null=True, blank=True)
    car_park = models.FloatField(null=True, blank=True, verbose_name="Car park/ Car porch")
    material_functional_test = models.FloatField(null=True, blank=True, verbose_name="Material & Functional Test")
    
    total = models.FloatField(null=True, blank=True, verbose_name="Total (1.1-5)")
    me_fittings = models.FloatField(null=True, blank=True, verbose_name="Basic M&E Fittings")
    mock_up_score = models.FloatField(null=True, blank=True, verbose_name="QLASSIC score with mock up")
    qlassic_score = models.FloatField(null=True, blank=True, verbose_name="QLASSIC score")

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, blank=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, blank=True, max_length=50)

    def __str__(self):
        return str(self.qaa) if self.qaa else ''

    def calculate_sample(self):
        sample = 0
        if self.number_of_sample == None or self.number_of_sample == 0:
            gfa = self.qaa.pi.gfa
            gfa_per = 70
            min = 30
            max = 700
            building_type = self.qaa.building_type
            if building_type == 'A':
                gfa_per = 70
                min = 30
                max = 700
            if building_type == 'B':
                gfa_per =  70
                min = 30
                max = 600
            if building_type == 'C':
                gfa_per = 500
                min = 30
                max = 150
            if building_type == 'D':
                gfa_per = 500
                min = 30
                max = 100

            sample = gfa / gfa_per
            if sample < min:
                sample = min
            elif sample > max:
                sample = max
            else:
                pass
            self.number_of_sample = round(sample)
            self.save()
        else:
            sample = self.number_of_sample

        return round(sample)

    # category A&B: P 40% S 40% C 20% daripada total sample
    # category C&D: P 60% S 15% C 25% dariapda total sample
    def get_ptotal(self):
        total = 0
        if self.ptotal == None or self.ptotal == 0:
            ab = 0.4
            cd = 0.6
            if self.qaa.building_type == 'A' or self.qaa.building_type == 'B':
                total = self.calculate_sample() * ab
            elif self.qaa.building_type == 'C' or self.qaa.building_type == 'D':
                total = self.calculate_sample() * cd
            self.ptotal = total
            self.save()
        else:
            total = self.ptotal
        return round(total)
    
    def get_stotal(self):
        total = 0
        if self.stotal == None or self.stotal == 0:
            ab = 0.4
            cd = 0.15
            if self.qaa.building_type == 'A' or self.qaa.building_type == 'B':
                total = self.calculate_sample() * ab
            elif self.qaa.building_type == 'C' or self.qaa.building_type == 'D':
                total = self.calculate_sample() * cd
            self.stotal = total
            self.save()
        else:
            total = self.stotal
        return round(total)
    
    def get_ctotal(self):
        total = 0
        if self.ctotal == None or self.ctotal == 0:
            ab = 0.2
            cd = 0.25
            if self.qaa.building_type == 'A' or self.qaa.building_type == 'B':
                total = self.calculate_sample() * ab
            elif self.qaa.building_type == 'C' or self.qaa.building_type == 'D':
                total = self.calculate_sample() * cd
            self.ctotal = total
            self.save()
        else:
            total = self.ctotal
        return round(total)

class SupportingDocuments(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    jt = models.ForeignKey(JoinedTraining, on_delete=models.CASCADE, null=True, blank=True)
    ra = models.ForeignKey(RoleApplication, on_delete=models.CASCADE, null=True, blank=True)
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True, blank=True)
    
    file_name = models.CharField(null=True, max_length=255)
    file = models.FileField(null=True, max_length=255, upload_to=PathAndRename('documents'), validators=[file_size_validator])
    reviewed_file = models.FileField(null=True, max_length=255, upload_to=PathAndRename('documents/reviewed'), validators=[file_size_validator])
    
    upload_date = models.DateTimeField(auto_now_add=True)

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)
   
    def __str__(self):
        return str(self.id)

class SuggestedAssessor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True)
    assessor = models.ForeignKey(Assessor, on_delete=models.CASCADE, null=True)
    # pi = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE, null=True)
    
    project_location = models.CharField(null=True, max_length=255)
    assessor_no = models.CharField(null=True, max_length=255, verbose_name="Assessor number")
    role_in_project = models.CharField(null=True, max_length=255)

    ACCEPTION = [
        # To follow SRS
        ('accept','Accept'),
        ('reject','Reject'),
        ('pending','Wait For Respond'),
    ]
    acception = models.CharField(
        null=True,
        blank=True,
        choices=ACCEPTION,
        max_length=10
    )

    prev_acception = models.CharField(
        null=True,
        blank=True,
        choices=ACCEPTION,
        max_length=10
    )


    remarks = models.TextField(null=True, blank=True, max_length=255)

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)
   
    def __str__(self):
        return str(self.id)

class AssignedAssessor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessor = models.ForeignKey(Assessor, on_delete=models.CASCADE, null=True)
    ad = models.ForeignKey(AssessmentData, on_delete=models.CASCADE, null=True)

    assessor_number = models.CharField(null=True, max_length=255)
    name = models.CharField(null=True, max_length=255)
    
    ROLE_IN_ASSESSMENT = [
        # To follow SRS
        ('lead_assessor','Lead Assessor'),
        ('assessor','Assessor'),
    ]
    role_in_assessment = models.CharField(
        default='assessor',
        null=True,
        choices=ROLE_IN_ASSESSMENT,
        max_length=30
    )

    complete = models.BooleanField(null=True,blank=True,default=False)

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)
   
    def __str__(self):
        return self.name

class WorkCompletionForm(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True)
    assessor = models.ForeignKey(Assessor, on_delete=models.CASCADE, blank=True, null=True)
    assessor_number = models.CharField(blank=True, null=True, max_length=255)
    
    # pi = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE, blank=True, null=True)
    # ad = models.ForeignKey(AssessmentData, on_delete=models.CASCADE, blank=True, null=True)
   
    qaa_number = models.CharField(blank=True, null=True, max_length=255, verbose_name="QLASSIC Assessment Application number")
    coordinate = models.CharField(blank=True, null=True, max_length=255)
    weather = models.CharField(blank=True, null=True, max_length=255)
    
    name = models.CharField(blank=True, null=True, max_length=255)
    icno = models.CharField(blank=True, null=True, max_length=12, verbose_name="IC number (without '-')")
    company = models.CharField(blank=True, null=True, max_length=255)
    position = models.CharField(blank=True, null=True, max_length=255)
    hp_no = models.CharField(blank=True, null=True, max_length=255, verbose_name="Contact number")
    email = models.CharField(blank=True, null=True, max_length=255)
    
    signature = models.FileField(null=True,blank=True, max_length=500, upload_to=PathAndRename('qaa/signature'))

    # project_location = models.CharField(blank=True, null=True, max_length=255)
    assessment_start_date = models.DateField(blank=True, null=True, verbose_name='Assessment start date')
    assessment_end_date = models.DateField(blank=True, null=True, verbose_name='Assessment end date')
    number_of_sample = models.IntegerField(blank=True, null=True)
    number_of_form_used = models.IntegerField(blank=True, null=True)

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)
   
    def __str__(self):
        return str(self.name)

class QlassicReporting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code_id = models.CharField(null=True,blank=True, max_length=50)

    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True)

    report_number = models.CharField(null=True, max_length=255)
    
    REPORT_TYPE = [
        # To follow SRS
        ('qlassic_score_letter','QLASSIC Score Letter'),
        ('qlassic_certificate','QLASSIC Certificate'),
        ('qlassic_report','QLASSIC Report'),
    ]
    report_type = models.CharField(
        null=True,
        choices=REPORT_TYPE,
        max_length=30
    )

    report_file = models.FileField(null=True, blank=True, upload_to=PathAndRename('assessment/report/'), verbose_name='Report File')
    qr_file = models.ImageField(null=True, blank=True, upload_to=PathAndRename('assessment/qr/'), verbose_name='QR File')
    
    reviewed_by = models.CharField(null=True, blank=True, max_length=200)
    reviewed_date = models.DateTimeField(null=True, blank=True)
    verified_by = models.CharField(null=True, blank=True, max_length=200)
    verified_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.CharField(null=True, blank=True, max_length=200)
    approved_date = models.DateTimeField(null=True, blank=True)
    
    
    # Date
    created_by = models.CharField(null=True, max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)
   
    def __str__(self):
        return '%s' % (self.qaa)

    def save(self,*args, **kwargs):

        # rename file here
        

        if not self.code_id:
            prefix = 'QLA/REP/'
            prev_instances = self.__class__.objects.filter(code_id__contains=prefix).order_by('-created_date')
            if prev_instances.exists():
                last_instance_id = prev_instances.first().code_id.replace(prefix,'')
                self.code_id = prefix+'{0:05d}'.format(int(last_instance_id)+1)
            else:
                self.code_id = prefix+'{0:05d}'.format(1)
            
        super(QlassicReporting, self).save(*args, **kwargs)

class SiteAttendance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True)
    qaa_no = models.CharField(null=True, max_length=255, verbose_name="QLASSIC Assessment Application number")
    
    name = models.CharField(null=True, max_length=255)
    position = models.CharField(null=True, max_length=255)
    hp_no = models.CharField(null=True, max_length=255, verbose_name="Contact number")
    company = models.CharField(null=True, max_length=255)
    signature = models.FileField(null=True,blank=True, max_length=500, upload_to=PathAndRename('qaa/signature'))
    
    assessment_date = models.DateField(null=True, verbose_name='Assessment date')
    
    def __str__(self):
        return self.qaa_no

class SyncResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True)
    result = models.CharField(null=True,blank=True, default="[]", max_length=3000)
    label = models.CharField(null=True,blank=True, default="[]", max_length=3000)
    assessor = models.CharField(null=True,blank=True, max_length=255)
    coordinate = models.CharField(null=True,blank=True, max_length=255)
    sync_complete = models.BooleanField(null=True,blank=True,default=False)

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

class SampleResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True)
    sync = models.ForeignKey(SyncResult, on_delete=models.CASCADE, null=True)
    sync_code = models.CharField(null=True,blank=True, max_length=255)
    
    element_name = models.CharField(null=True,blank=True, max_length=255)
    element_code = models.CharField(null=True,blank=True, max_length=255)
    block = models.CharField(null=True,blank=True, max_length=255)
    unit = models.CharField(null=True,blank=True, max_length=255)
    period = models.CharField(null=True,blank=True, max_length=255)
    test_type = models.CharField(null=True,blank=True, max_length=255)
    selection_value = models.CharField(null=True,blank=True, max_length=255)
    sample_id = models.CharField(null=True,blank=True, max_length=255)
    sample_run = models.CharField(null=True,blank=True, max_length=1000)
    remark = models.TextField(null=True,blank=True, max_length=2000)
    partners = models.CharField(null=True,blank=True, max_length=4000)
    assessor_name = models.CharField(null=True,blank=True, max_length=255)
    assessor_id = models.CharField(null=True,blank=True, max_length=255)
    photo_1 = models.FileField(null=True,blank=True, max_length=500, upload_to=PathAndRename('qaa/photos1'))
    photo_2 = models.FileField(null=True,blank=True, max_length=500, upload_to=PathAndRename('qaa/photos2'))
    photo_3 = models.FileField(null=True,blank=True, max_length=500, upload_to=PathAndRename('qaa/photos3'))
    photo_4 = models.FileField(null=True,blank=True, max_length=500, upload_to=PathAndRename('qaa/photos4'))
    
    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True,blank=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True,blank=True, max_length=50)


class ElementResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sync = models.ForeignKey(SyncResult, on_delete=models.CASCADE, null=True)
    sync_code = models.CharField(null=True,blank=True, max_length=255)
    
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True)
    sample_result = models.ForeignKey(SampleResult, on_delete=models.CASCADE, null=True,blank=True)
    
    element_name = models.CharField(null=True,blank=True, max_length=255)
    element_code = models.CharField(null=True,blank=True, max_length=255)
    dg_name = models.CharField(null=True,blank=True, max_length=255)
    test_type = models.CharField(null=True,blank=True, max_length=255)

    result = models.CharField(null=True,blank=True, max_length=2000)
    total_compliance = models.IntegerField(null=True,default=0)
    total_check = models.IntegerField(null=True,default=0)
    
    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True,blank=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True,blank=True, max_length=50)

# Deprecated
class SubComponentResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_component = models.ForeignKey(SubComponent, on_delete=models.CASCADE, null=True)
    assessment_data = models.ForeignKey(AssessmentData, on_delete=models.CASCADE, null=True)

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    def __str__(self):
        return '%s' % (self.assessment_data)

# Deprecated
class SubComponentResultDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sub_component_result = models.ForeignKey(SubComponentResult, on_delete=models.CASCADE, null=True)
    file_name = models.CharField(null=True, max_length=255)
    file = models.FileField(null=True, max_length=255, upload_to=PathAndRename('results'))

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)
   
    def __str__(self):
        return self.file_name


# Deprecated
class DefectGroupResult(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    defect_group = models.ForeignKey(DefectGroup, on_delete=models.CASCADE, null=True)
    assessment_data = models.ForeignKey(AssessmentData, on_delete=models.CASCADE, null=True)

    SCORE = [
        # To follow SRS
        (0,'Fail'),
        (1,'Pass'),
    ]
    score = models.IntegerField(
        null=True,
        default=0,
        choices=SCORE,
    )

    applicable = models.BooleanField(default=True)
    
    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    def __str__(self):
        return '%s' % (self.assessment_data)

class Scope(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True, blank=True)
    scope = models.TextField(null=True)

    def __str__(self):
        return self.scope


class Survey(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(max_length=100, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    comment = models.TextField()

    def __str__(self):
        return self.user.email
    

from django.db import models
from users.models import CustomUser
import uuid

# Helpers
from core.helpers import PathAndRename, STATE_CHOICES

PROJECT_TYPE = [
    # To follow SRS
    ('PRIVATE','PRIVATE'),
    ('GOVERNMENT','GOVERNMENT'),
]

PROJECT_STATUS = [
        ('reviewed','Reviewed'),
        ('verified','Verified'),
        ('rejected','Rejected'),
        ('is_being_assessed','is being assessed'),
        ('completed','Completed'),
    ]

# Create your models here.
class ProjectInfo(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # qaa = models.ForeignKey(QlassicAssessmentApplication, on_delete=models.CASCADE, null=True)
    
    RATING_TYPE = [
        # To follow SRS
        ('qlassic','QLASSIC'),
        #('mock_up','Mock up'),
    ]
    rating_type = models.CharField(
        null=True,
        choices=RATING_TYPE,
        max_length=10
    )

    project_title = models.CharField(null=True, max_length=2000)
    
 
    
    project_type = models.CharField(
        null=True,
        choices=PROJECT_TYPE,
        max_length=10,
        verbose_name="Project type @ Sector"
    )

    levy_number = models.CharField(null=True, max_length=10)
    levy_receipt = models.FileField(null=True, blank=True, max_length=255, upload_to=PathAndRename('documents'))
    gfa = models.FloatField(null=True, verbose_name="Gross Floor Area (meter square)")
    phase = models.CharField(null=True, max_length=10, verbose_name="Project phase")
    # contract_value = models.CharField(null=True, max_length=5, verbose_name="Contract value (RM including GST)")
    contract_value = models.DecimalField(null=True, max_digits=20, decimal_places=2, verbose_name="Contract value (RM including GST)")
    project_location = models.CharField(choices=STATE_CHOICES, null=True, max_length=255)
    project_reference_number = models.CharField(null=True, max_length=255)
    project_manager = models.CharField(null=True, max_length=255)
    developer = models.CharField(null=True, max_length=255)
    developer_ssm_number = models.CharField(null=True, max_length=50)
    architect_firm = models.CharField(null=True, max_length=255)
    structural_civil_engineer_firm = models.CharField(null=True, max_length=255, verbose_name="Structural & Civil Engineer Firm")
    mechanical_electrical_firm = models.CharField(null=True, max_length=255, verbose_name="M&E Engineer Firm")
    contractor_name = models.CharField(null=True, max_length=255)
    contractor_cidb_registration_no = models.CharField(null=True, max_length=255)
    CONTRACTOR_REGISTRATION_GRADE = [
        # To follow SRS
        ('G1','G1'),
        ('G2','G2'),
        ('G3','G3'),
        ('G4','G4'),
        ('G5','G5'),
        ('G6','G6'),
        ('G7','G7'),
    ]
    contractor_registration_grade = models.CharField(
        null=True,
        choices=CONTRACTOR_REGISTRATION_GRADE,
        max_length=3
    )

    site_representative = models.CharField(null=True, max_length=255)
    hp_no = models.CharField(null=True, max_length=15, verbose_name='Contact number')
    email = models.CharField(null=True, max_length=50)
    
    ISO9001 = [
        # To follow SRS
        ('yes','Yes'),
        ('no','No'),
    ]
    iso9001 = models.CharField(
        null=True,
        choices=ISO9001,
        max_length=4,
        verbose_name='Does the project have ISO 9001?'
    )

    SHASSIC = [
        # To follow SRS
        ('yes','Yes'),
        ('no','No'),
    ]
    shassic = models.CharField(
        null=True,
        choices=SHASSIC,
        max_length=4,
        verbose_name='Does the project have SHASSIC?'
    )

    BIM = [
        # To follow SRS
        ('yes','Yes'),
        ('no','No'),
    ]
    bim = models.CharField(
        null=True,
        choices=BIM,
        max_length=4,
        verbose_name='Does the project have BIM?'
    )

    GBI = [
        # To follow SRS
        ('yes','Yes'),
        ('no','No'),
    ]
    gbi = models.CharField(
        null=True,
        choices=GBI,
        max_length=4,
        verbose_name='Does the project have GBI?'
    )

    MYCREST = [
        # To follow SRS
        ('yes','Yes'),
        ('no','No'),
    ]
    mycrest = models.CharField(
        null=True,
        choices=MYCREST,
        max_length=4,
        verbose_name='Does the project have MyCREST?'
    )

    CONSTRUCTION_METHOD = [
        # To follow SRS
        ('ibs','IBS'),
        ('conventional','Conventional'),
        ('design_and_build','Design & Build'),
        ('pfi','PFI'),
    ]
    construction_method = models.CharField(
        null=True,
        choices=CONSTRUCTION_METHOD,
        max_length=50
    )

    ibs_percentage = models.DecimalField(null=True, blank=True, max_digits=10, decimal_places=2, verbose_name="IBS percentage (%)")

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)
   
    def __str__(self):
        return '%s' % (self.project_title)

# class Developer(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     pi = models.ForeignKey(ProjectInfo, on_delete=models.CASCADE, blank=True)
    
#     name = models.CharField(blank=True, max_length=255)
#     address1 = models.CharField(blank=True, max_length=255)
#     address2 = models.CharField(blank=True, max_length=255)
#     postcode = models.IntegerField(blank=True)
#     city = models.CharField(blank=True, max_length=255)
#     state = models.CharField(blank=True, max_length=255)
#     company_registration_number = models.CharField(blank=True, max_length=255)
#     representative_name = models.CharField(blank=True, max_length=255)
#     representative_email = models.CharField(blank=True, max_length=255)
#     representative_hp_number = models.CharField(blank=True, max_length=255)

#     # Date
#     created_date = models.DateTimeField(auto_now_add=True)
#     modified_date = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.name

class Contractor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)


    project_status = models.CharField(
        null=True,
        choices=PROJECT_STATUS,
        max_length=50
    )
 
    name_of_contractor = models.CharField(null=True, blank=True, max_length=255)
    contractor_registration_number = models.CharField(null=True, blank=True, max_length=255)

    CONTRACTOR_REGISTRATION_GRADE = [
        # To follow SRS
        ('G1','G1'),
        ('G2','G2'),
        ('G3','G3'),
        ('G4','G4'),
        ('G5','G5'),
        ('G6','G6'),
        ('G7','G7'),
    ]
    contractor_registration_grade = models.CharField(
        null=True, 
        blank=True,
        choices=CONTRACTOR_REGISTRATION_GRADE,
        max_length=3
    )

    project_type = models.CharField(
        null=True, 
        blank=True,
        choices=PROJECT_TYPE,
        max_length=10,
        verbose_name="Project type @ Sector"
    )
    CONTRACT_TYPE = [
        # To follow SRS
        ('lump_sum','Lump Sum'),
        ('provisional_quantity','Provisional Quantity'),
        ('lum_sump_and_quantity','Lump Sum and Quantity'),
    ]
    contract_type = models.CharField(
        null=True, blank=True,
        choices=CONTRACT_TYPE,
        max_length=50
    )

    # qaa_number = models.CharField(null=True, blank=True, max_length=50, verbose_name='Qlassic Assessment Application number')

    levy_number = models.CharField(null=True, blank=True, max_length=50)
    ssm_number = models.CharField(null=True, blank=True, max_length=50, verbose_name='SSM number')
    # contract_value = models.CharField(null=True, blank=True, max_length=10, verbose_name="Contract value (RM including GST)")
    contract_value = models.DecimalField(null=True, blank=True, max_digits=20, decimal_places=2, verbose_name="Contract value (RM including GST)")

    project_title = models.CharField(null=True, blank=True, max_length=2000)
    project_location = models.CharField(choices=STATE_CHOICES, null=True, blank=True, max_length=255)
    project_reference_number = models.CharField(null=True, blank=True, max_length=255)

    letter_of_award_date = models.DateField(null=True, blank=True, verbose_name='Letter of Award Date')
    start_date = models.DateField(null=True, blank=True, verbose_name='Start Date')
    dateline = models.DateField(null=True, blank=True, verbose_name='Dateline')
    
    client_name = models.CharField(null=True, blank=True, max_length=255)
    registered_address = models.CharField(null=True, blank=True, max_length=255)
    registered_postcode = models.CharField(null=True, blank=True, max_length=10, verbose_name='Postal code')
    registered_city = models.CharField(null=True, blank=True, max_length=255)
    registered_state = models.CharField(choices=STATE_CHOICES, null=True, blank=True, max_length=255)    

    correspondence_address = models.CharField(null=True, blank=True, max_length=255)
    correspondence_postcode = models.CharField(null=True, blank=True, max_length=10, verbose_name='Postal code')
    correspondence_city = models.CharField(null=True, blank=True, max_length=255)
    correspondence_state = models.CharField(choices=STATE_CHOICES, null=True, blank=True, max_length=255)    
    
    applied = models.BooleanField(default=False)
    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, blank=True, max_length=255)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return self.name_of_contractor

class VerifiedContractor(models.Model):
    user = models.ForeignKey(CustomUser, unique=True, on_delete=models.CASCADE, null=True)
    ssm_number = models.CharField(null=True, max_length=255)
    contractor_registration_number = models.CharField(null=True, max_length=255)
    is_verified = models.BooleanField(default=True)

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)


class SubmitFeedback(models.Model):
    user = models.ForeignKey(CustomUser, blank=True, on_delete=models.CASCADE, null=True)
    name = models.CharField(null=True, blank=True, max_length=200)
    email = models.CharField(null=True, blank=True, max_length=50)
    comment = models.TextField(null=True, blank=True, max_length=3000)
    

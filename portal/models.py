from django.db import models
import uuid

from core.helpers import PathAndRename, STATE_CHOICES
from .helpers import TEMPLATE_TYPE

# Models
from trainings.models import TrainingType
from users.models import CustomUser


from core.helpers import (
    PathAndRename, 
    STATE_CHOICES, 
    file_size_validator,
)

# Create your models here.
class Announcement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(null=True, max_length=255)
    announcement = models.TextField(null=True, max_length=3000)
 
    PUBLISH = [
        # To follow SRS
        ('publish', 'Publish'),
        ('do_not_publish', 'Do not publish'),
    ]
    publish = models.CharField(
        null=True,
        max_length=50,
        choices=PUBLISH
    )

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    def __str__(self):
        return self.title

class Publication(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(null=True, max_length=255)
    publication = models.TextField(null=True, max_length=3000)
    file = models.FileField(max_length=255, null=True, upload_to=PathAndRename('publications'))
    
    PUBLISH = [
        # To follow SRS
        ('publish', 'Publish'),
        ('do_not_publish', 'Do not publish'),
    ]
    publish = models.CharField(
        null=True,
        max_length=50,
        choices=PUBLISH
    )

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    def __str__(self):
        return self.title

class Training(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name_of_training = models.CharField(null=True, max_length=255, verbose_name="Training Name")
    
    from_date = models.DateField(null=True, verbose_name='Start Date')
    to_date = models.DateField(null=True, verbose_name='End Date')
    available_seat = models.IntegerField(null=True, verbose_name='Available Seat')
    passing_mark = models.DecimalField(null=True, max_digits=6, decimal_places=2, verbose_name="Passing Mark")
    ccd_point = models.DecimalField(null=True, max_digits=6, decimal_places=2, verbose_name="CCD Point")
    fee = models.DecimalField(null=True, max_digits=8, decimal_places=2, verbose_name="Fees")

    address1 = models.CharField(null=True, max_length=100)
    address2 = models.CharField(null=True, max_length=100)
    postcode = models.CharField(null=True, max_length=10, verbose_name='Postal code')
    city = models.CharField(null=True, max_length=50)
    state = models.CharField(choices=STATE_CHOICES, null=True, max_length=50)    

    publish = models.BooleanField(default=False, verbose_name="Published?")

    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    def __str__(self):
        return self.name_of_training

class LetterTemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(null=True, max_length=255)
    
    # If exist, it considered as training template, else considered as general template
    training_type = models.ForeignKey(TrainingType, on_delete=models.CASCADE, null=True, blank=True)
    
    template_file = models.FileField(null=True, blank=True, upload_to=PathAndRename('templates'))
    is_active = models.BooleanField(default=True, verbose_name="Use this template now?")

    template_type = models.CharField(
        null=True,
        max_length=150,
        choices=TEMPLATE_TYPE
    )


    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    def __str__(self):
        return '%s' % (self.title)

class LetterTemplateConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.CharField(null=True, max_length=255)
    
    value = models.TextField(null=True, blank=True, max_length=3000)
  
    # Date
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(null=True, max_length=50)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.CharField(null=True, max_length=50)

    def __str__(self):
        return '%s' % (self.slug)


class UpdateInformation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    update_logo = models.FileField(null=True, blank=True, upload_to=PathAndRename('logo'), validators=[file_size_validator])
    update_footer_logo = models.FileField(null=True, blank=True, upload_to=PathAndRename('logo'), validators=[file_size_validator])
    update_hyperlink = models.URLField(null=True, blank=True, max_length=2000)
    update_address = models.TextField(null=True, blank=True, max_length=5000)





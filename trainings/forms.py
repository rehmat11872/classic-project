from django.forms import ModelForm
from django import forms

from .models import (
    RoleApplication, Training, 
    RegistrationTraining, 
    Coach, 
    TrainingType,
    Feedback,
)

class EditRoleApplicationForm(ModelForm):
    class Meta:
        model = RoleApplication
        fields ='__all__'

class TrainingCreateForm(ModelForm):
    # from_date = forms.DateField(
    #     widget=forms.DateInput(
    #         attrs={
    #             'class': 'datepicker',
    #             'placeholder':'dd/mm/yyyy'
    #         } 
    #     )
    # )
    # to_date = forms.DateField(
    #     widget=forms.DateInput(
    #         attrs={
    #             'class': 'datepicker',
    #             'placeholder':'dd/mm/yyyy'
    #         } 
    #     )
    # )
    class Meta:
        model = Training
        fields = (
            'training_name',
            'from_date',
            'to_date',
            'from_time',
            'to_time',
            'training_type',
            'size',
            'passing_mark',
            'ccd_point',
            'fee',
            'cert_type',
            'address1',
            'address2',
            'postcode',
            'city',
            'state',
            'publish',
        )

class RegistrationTrainingCreateForm(ModelForm):
    class Meta:
        model = RegistrationTraining
        fields = (
            'participant_name',
            'participant_icno',
            'participant_email',
            'participant_hpno',
            'participant_designation',
            'participant_organization',
            'participant_organization_type',
        )

class TrainingTypeCreateForm(ModelForm):
    class Meta:
        model = TrainingType
        fields = (
            'name',
            'cert_type',
            'required_for_assessor',
        )

class RegistrationTrainingReviewForm(ModelForm):
    class Meta:
        model = RegistrationTraining
        fields = (
            'payment_mode',
            'amount',
            'remarks',
        )

class CoachCreateForm(ModelForm):
    class Meta:
        model = Coach
        fields = (
            'email',
            'name',
            'hp_no',
        )

class RoleApplicationSupportingDocumentsUploadForm(forms.Form):
    sd_ra_1 = forms.FileField(required=False)
    sd_ra_2 = forms.FileField(required=False)
    sd_ra_3 = forms.FileField(required=False)
    sd_ra_4 = forms.FileField(required=False)
    sd_ra_5 = forms.FileField(required=False)
    sd_ra_6 = forms.FileField(required=False)

class AttendanceSheetUploadForm(ModelForm):
    class Meta:
        model = Training
        fields = {
            'attendance_sheet_file',
        }

class FeedbackCreateForm(ModelForm):
    class Meta:
        model = Feedback
        fields = {
            'description_1',
            'description_2',
        }

class RoleApplicationInterviewForm(ModelForm):
    class Meta:
        model = RoleApplication
        fields = {
            'interview_date',
            'interview_time_from',
            'interview_time_to',
            'interview_location',
        }
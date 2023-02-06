from django.forms import ModelForm
from django import forms

from .models import ProjectInfo, VerifiedContractor
from assessments.models import QlassicAssessmentApplication

class ProjectInfoCreateForm(ModelForm):
    levy_receipt = forms.FileField(
        label="Levy receipt",
        required=True
    )
    class Meta:
        model = ProjectInfo
        fields = '__all__'

class ProjectInfoApplicationForm(ModelForm):
    class Meta:
        model = ProjectInfo
        fields = (
            'rating_type',
            'project_manager',
            'project_type',
            'levy_receipt',
            'developer',
            'developer_ssm_number',
            'iso9001',
            'shassic',
            'bim',
            'mycrest',
            'gfa',
            'architect_firm',
            'structural_civil_engineer_firm',
            'mechanical_electrical_firm',
            'site_representative',
            'email',
            'hp_no',
            'construction_method',
            'ibs_percentage',
        )

class VerifiedContractorForm(ModelForm):
    class Meta:
        model = VerifiedContractor
        fields = (
            'user',
            'ssm_number',
            'contractor_registration_number',
        )

class EditApplicationForm(ModelForm):
    class Meta:
        model = QlassicAssessmentApplication
        fields = '__all__'       
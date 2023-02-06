from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm
from django import forms

from .models import CustomUser, WorkExperience, AcademicQualification


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CustomUser
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ('email',)

class RoleUpdateForm(ModelForm):

    class Meta:
        model = CustomUser
        fields = ('role',)

class UserUpdateForm(ModelForm):
    greencard_exp_date = forms.DateField(
        required=False,
        label="Green card exp. date",
    )
    icno = forms.CharField(
        label="IC Number",
        widget=forms.TextInput(
            attrs={
                'placeholder':'eg. 910101-22-3333'
            } 
        )
    )
    class Meta:
        model = CustomUser
        exclude = (
            'code_id',
            'password',
            'qia_status',
            'email',
            'last_login',
            'groups',
            'is_superuser',
            'user_permissions',
            'first_name',
            'last_name',
            'qia_payment_mode',
            'qia_payment_status',
            'is_staff',
            'is_active',
            'date_joined',
            'role',
            'created_by',
            'modified_by',
        )
        fields = '__all__'

class WorkExperienceCreateForm(ModelForm):
    year_from = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'placeholder':'eg. 2010',
            } 
        )
    )
    year_to = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'placeholder':'eg. 2010',
            } 
        )
    )
    class Meta:
        model = WorkExperience
        fields = '__all__'
        exclude = (
            'user',
            'created_by',
            'modified_by',
        )

class AcademicQualificationCreateForm(ModelForm):
    year = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'placeholder':'eg. 2010'
            } 
        )
    )
    class Meta:
        model = AcademicQualification
        fields = '__all__'
        exclude = (
            'user',
            'created_by',
            'modified_by',
        )
class AcademicQualificationCreateForm(ModelForm):
    year = forms.CharField(
        widget=forms.NumberInput(
            attrs={
                'placeholder':'eg. 2010'
            } 
        )
    )
    class Meta:
        model = AcademicQualification
        fields = '__all__'
        exclude = (
            'user',
            'created_by',
            'modified_by',
        )

class TransportUpdateForm(ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            'transport_model',
            'transport_cc',
            'transport_registration_number',
        )
from django.forms import ModelForm
from django import forms

from .models import Announcement, Publication, Training, LetterTemplate


class AnnouncementCreateForm(ModelForm):
    class Meta:
        model = Announcement
        fields = '__all__'
        exclude = ['created_by','modified_by']

class PublicationCreateForm(ModelForm):
    class Meta:
        model = Publication
        fields = '__all__'
        exclude = ['created_by','modified_by']

class TrainingCreateForm(ModelForm):

    class Meta:
        model = Training
        fields = '__all__'
        exclude = ['created_by','modified_by']

class LetterTemplateCreateForm(ModelForm):
    class Meta:
        model = LetterTemplate
        fields = (
            'title',
            'template_file',
            'template_type',
            'is_active',
        )
    
class LetterTemplateTrainingCreateForm(ModelForm):
    template_file = forms.FileField(required=True)
    class Meta:
        model = LetterTemplate
        fields = (
            'template_file',
        )
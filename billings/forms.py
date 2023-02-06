from django.forms import ModelForm
from django import forms

from .models import ClaimApplication


class ClaimMileageCreateForm(ModelForm):

    class Meta:
        model = ClaimApplication
        fields = (
            'claim_category',
            'date_from',
            'time_from',
            'time_to',
            'location_from',
            'state_from',
            'location_to',
            'state_to',
            'mileage',
            'notes',
        )

class ClaimFiCreateForm(ModelForm):

    class Meta:
        model = ClaimApplication
        fields = (
            'claim_category',
            'date_from',
            'date_to',
        )

class ClaimPublicTransportCreateForm(ModelForm):

    class Meta:
        model = ClaimApplication
        fields = (
            'claim_category',
            'transport_type',
            'date_of_transaction',
            'receipt_number',
            'total_receipt_amount',
            'attachments',
        )

class ClaimAccommodationCreateForm(ModelForm):

    class Meta:
        model = ClaimApplication
        fields = (
            'claim_category',
            'accommodation_type',
            'date_of_transaction',
            'receipt_number',
            'total_receipt_amount',
            'attachments',
        )

class ClaimOthersCreateForm(ModelForm):

    class Meta:
        model = ClaimApplication
        fields = (
            'claim_category',
            'notes',
            'date_of_transaction',
            'receipt_number',
            'total_receipt_amount',
            'attachments',
        )
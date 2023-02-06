# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from core.helpers import STATE_CHOICES
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404
from django.http import HttpResponse
from django.db.models import Q
import datetime
import random

# Models
from billings.models import ClaimApplication
from assessments.models import QlassicAssessmentApplication, AssignedAssessor
from trainings.models import Training
from users.models import Assessor

# Forms
from users.forms import TransportUpdateForm

# Helpers
from .helpers import get_claim_category_name

# Decorators
from authentication.decorators import allowed_users

# Create your views here.

### Claim Module ###
@login_required(login_url="/login/")
def dashboard_claim_dashboard(request, role):
    claims = ClaimApplication.objects.all().filter(user=request.user).order_by('-created_date')
    transport_form = TransportUpdateForm(instance=request.user)
    context = {
        'role': role,
        'claims': claims,
        'transport_form': transport_form,
    }

    if request.method == 'POST':
        if 'transport' in request.POST:
            transport_form = TransportUpdateForm(request.POST, instance=request.user)
            if transport_form.is_valid():
                transport_form.save()
                messages.info(request, 'Updated successfully.')
            else:
                messages.warning(request, 'Unable to update the transport information.')
        return redirect('dashboard_claim_dashboard', role)

    return render(request, "dashboard/claim/dashboard.html", context)

@login_required(login_url="/login/")
def dashboard_claim_project_list(request, role, category):
    category_name = get_claim_category_name(category)
    claims = ClaimApplication.objects.all().filter(user=request.user, claim_category=category).order_by('-created_date')
    assigned = None
    trainings = None

    if role == 'assessor':
        # assessor_projects = QlassicAssessmentApplication.objects.all().filter(
        #     # user=request.user
        #     Q(user=request.user,application_status='completed')|
        #     Q(user=request.user,application_status='approved')
        # )
        assessor = Assessor.objects.all().filter(user=request.user)
        if len(assessor) > 0:
            assessor_single = assessor[0]
            assigned = AssignedAssessor.objects.all().filter(assessor=assessor_single)
    if role == 'trainer':
        trainings = Training.objects.all().filter(trainer=request.user,attendance_review_status='approved')
    context = {
        'role': role,
        'claims': claims,
        'category': category,
        'category_name': category_name,
        'assigned': assigned,
        'trainings': trainings,
    }
    return render(request, "dashboard/claim/project_list.html", context)

from .forms import (
    ClaimMileageCreateForm, 
    ClaimFiCreateForm,
    ClaimPublicTransportCreateForm,
    ClaimAccommodationCreateForm,
    ClaimOthersCreateForm,
)

@login_required(login_url="/login/")
def dashboard_claim_application(request, role, category, id):
    category_name = get_claim_category_name(category)
    project = None
    training = None
    zone = ''
    if role == 'assessor':
        project = get_object_or_404(QlassicAssessmentApplication, id=id)
        if project.pi.project_location == request.user.state:
            zone = '1'
        else:
            zone = '2'
    if role == 'trainer':
        training = get_object_or_404(Training, trainer=request.user, id=id)
        if training.state == request.user.state:
            zone = '1'
        else:
            zone = '2'
    state_choices = STATE_CHOICES
    context = {
        'role': role,
        'zone': zone,
        'category': category,
        'category_name': category_name,
        'state_choices':state_choices,
        'project': project,
        'training': training,
        'transport_types': ClaimApplication._meta.get_field('transport_type').choices,
        'accommodation_types': ClaimApplication._meta.get_field('accommodation_type').choices,
    }

    if request.method == "POST":
        form = None
        if category == 'mileage':
            form = ClaimMileageCreateForm(request.POST)
        if category == 'fi':
            form = ClaimFiCreateForm(request.POST)
        if category == 'public_transport':
            form = ClaimPublicTransportCreateForm(request.POST, request.FILES)
        if category == 'accommodation':
            form = ClaimAccommodationCreateForm(request.POST, request.FILES)
        if category == 'others':
            form = ClaimOthersCreateForm(request.POST, request.FILES)
        
        if form.is_valid():
            data = form.save()
            
            data.zone = zone

            # Basic Requirement
            data.user = request.user
            data.transport_model = request.user.transport_model
            data.transport_cc = request.user.transport_cc
            data.transport_registration_number = request.user.transport_registration_number
            
            # Calculate Amount For Specific Claim
            if category == 'mileage':
                amount = calculate_mileage_claim_amount(data ,zone)
                data.total_receipt_amount = amount
            if category == 'fi':
                balance_date = data.date_to - data.date_from
                days = balance_date.days + 1
                if days > 0:
                    amount = calculate_fi_claim_amount(data ,role)
                    data.total_receipt_amount = amount
                else:
                    messages.warning(request, 'Please set the correct range.')
                    return redirect('dashboard_claim_application', role, category, id)
            # Assign qaa or training
            if role == 'assessor':
                data.qaa = project
            if role == 'trainer':
                data.training = training

            data.save()
            messages.info(request, 'Successfully applied the claim.')
            return redirect('dashboard_claim_dashboard', role)
        else:
            messages.warning(request, 'Problem with applying the claim:'+form.errors.as_text())
            return redirect('dashboard_claim_application', role, category, id)
    return render(request, "dashboard/claim/application.html", context)

def calculate_mileage_claim_amount(claim, zone):
    mileage = claim.mileage
    amount = 0.0
    if zone == '1':
        if mileage <= 150:
            amount = mileage * 0.70
        else:
            amount = 150 * 0.70
            amount += (mileage-150) * 0.60
    if zone == '2':
        if mileage <= 300:
            amount = mileage * 0.70
        else:
            amount = 300 * 0.70
            amount += (mileage-300) * 0.60
    return amount

def calculate_fi_claim_amount(claim, role):
    balance_date = claim.date_to - claim.date_from
    days = balance_date.days + 1
    amount = 0.0
    if role == 'assessor':
        amount = days * 350
    if role == 'trainer':
        amount = days * 1000
    return amount


@login_required(login_url="/login/")
def dashboard_claim_review_list(request, role):
    claims = None
    if role == 'assessor':
        claims = ClaimApplication.objects.all().exclude(qaa=None).order_by('-created_date')
    if role == 'trainer':
        claims = ClaimApplication.objects.all().exclude(training=None).order_by('-created_date')
    context = {
        'role': role,
        'claims': claims,
    }
    return render(request, "dashboard/claim/review_list.html", context)

@login_required(login_url="/login/")
def dashboard_claim_review(request, role, id, mode):
    claim = get_object_or_404(ClaimApplication, id=id)
    context = {
        'role': role,
        'claim': claim,
        'mode': mode,
    }

    if request.method == 'POST':
        if mode == 'verify':
            if 'accept' in request.POST:
                claim.claim_status = 'verified'
                claim.save()
                messages.info(request,'Successfully verified the claim application.')
            if 'reject' in request.POST:
                claim.claim_status = 'rejected'
                claim.save()
                messages.info(request,'Successfully rejected the claim application.')
        if mode == 'approve':
            if 'accept' in request.POST:
                claim.claim_status = 'approved'
                claim.save()
                messages.info(request,'Successfully approved the claim application.')
            if 'reject' in request.POST:
                claim.claim_status = 'rejected'
                claim.save()
                messages.info(request,'Successfully rejected the claim application.')
        return redirect('dashboard_claim_review_list', role)
    return render(request, "dashboard/claim/review.html", context)


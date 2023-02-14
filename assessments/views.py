"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404, HttpResponse, JsonResponse
from django.db.models import Q
import datetime
import random
import json

# Payment
from django.views.decorators.csrf import csrf_exempt
from api.soap.create_transaction import cancel_proforma, create_transaction, payment_gateway_url, get_receipt_url
from billings.helpers import payment_response_process, get_payment_history_url
from billings.models import Payment

import requests

from core.helpers import get_state_code, get_sector_code, send_email_default, get_domain
from .helpers import get_qaa_sd_name

# Forms
from users.forms import UserUpdateForm
from assessments.forms import QAACreateForm, QAAApplicationForm, QAAReviewForm, QAAVerifyForm, \
    SupportingDocumentsUploadForm, AddProjectForm, ViewProjectForm
from projects.forms import ProjectInfoCreateForm, ProjectInfoApplicationForm, EditApplicationForm

# Models
from users.models import Assessor, CustomUser
from projects.models import Contractor, VerifiedContractor, ProjectInfo
from assessments.models import (
    Component, ElementResult, SampleResult,
    SubComponent,
    Element,
    DefectGroup,
    QlassicAssessmentApplication,
    SupportingDocuments,
    SuggestedAssessor,
    AssignedAssessor,
    AssessmentData, SyncResult, WorkCompletionForm,
    Scope
)

# SOAP
from api.soap.get_contractor import get_project, verify_contractor

# Decorators
from authentication.decorators import allowed_users

from projects.models import SubmitFeedback

import xlwt
from io import BytesIO

from django.views.generic import TemplateView, View, CreateView
from django.urls import reverse
from .utils import CreateExcell


### Admin - Application Module ###
@login_required(login_url="/login/")
def dashboard_application_overview(request):
    return render(request, "dashboard/application/overview.html")


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_application(request):
    return render(request, "dashboard/application/list.html")


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['contractor'])
def dashboard_application_profile(request):
    user = request.user
    form_user = UserUpdateForm(instance=user)
    if request.method == 'POST':
        form_user = UserUpdateForm(request.POST, request.FILES or None, instance=user)
        if form_user.is_valid():
            form_user.save()
            messages.info(request, 'Updated successfully')
        else:
            messages.warning(request, 'Unable to update profile')
        return redirect('dashboard_application_profile')
    context = {'form_user': form_user}
    return render(request, "dashboard/application/profile.html", context)


# @login_required(login_url="/login/")
# def dashboard_application_project(request):

#     contractors = Contractor.objects.all().filter(qaa_number=None)

#     # GET Filter
#     sector = ''
#     if 'sector' in request.GET:
#         sector = request.GET['sector']
#         if filter != '':
#             contractors = contractors.filter(project_type=sector)

#     context = {
#         'sector':sector,
#         'contractors':contractors,
#     }
#     return render(request, "dashboard/application/project_list.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'contractor', 'applicant'])
def dashboard_application_project(request):
    # Check if verified contractor before displaying the list of contractor
    form = AddProjectForm()
    verified_contractor = VerifiedContractor.objects.filter(user=request.user, is_verified=True).first()
    contractors = None
    require_verification = False
    if verified_contractor == None:
        require_verification = True
    else:
        contractors = get_project(verified_contractor.contractor_registration_number)

    # GET Filter
    sector = ''
    if 'sector' in request.GET:
        sector = request.GET['sector']
        if sector != '':
            contractors = contractors.filter(project_type=sector)

    context = {
        'verified_contractor': verified_contractor,
        'require_verification': require_verification,
        'sector': sector,
        'contractors': contractors,
        'form': form
    }

    if request.method == 'POST':
        ssm_number = request.POST['ssm_number']
        contractor_registration_number = request.POST['contractor_registration_number']
        is_verify, error_message = verify_contractor(contractor_registration_number)
        if is_verify:
            VerifiedContractor.objects.create(
                user=request.user,
                ssm_number=ssm_number,
                contractor_registration_number=contractor_registration_number,
                is_verified=True,
                created_by=request.user.name,
                modified_by=request.user.name,
            )
            messages.info(request, 'Successfully verify the contractor profile')
        else:
            messages.warning(request, error_message)
        return redirect('dashboard_application_project')

    return render(request, "dashboard/application/project_list.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'contractor', 'applicant'])
def dashboard_application_new(request, contractor_registration_number, id):
    # contractor = get_object_or_404(Contractor, contractor_registration_number=contractor_registration_number, project_reference_number=id)
    contractor = Contractor.objects.filter(contractor_registration_number=contractor_registration_number,
                                           project_reference_number=id)[0]

    qaa = None
    pi = None
    create_new_qaa = False
    qaa_all = QlassicAssessmentApplication.objects.filter(
        pi__contractor_cidb_registration_no=contractor_registration_number, pi__project_reference_number=id).order_by(
        '-created_date')
    # qaa_all = QlassicAssessmentApplication.objects.all().filter(contractor=contractor).order_by('-created_date')
    if qaa_all.count() > 0:
        qaa = qaa_all[0]
        pi = qaa.pi
        if qaa.application_status == 'rejected':
            create_new_qaa = True
        elif qaa.application_status == 'rejected_amendment' or qaa.application_status == None or qaa.application_status == '':
            qaa = qaa
        else:
            messages.warning(request,
                             'Unable to apply QLASSIC. This project is already been registered in QLASSIC ASSESSMENT APPLICATION')
            return redirect('dashboard_application_project')

        if pi == None:
            pi = ProjectInfo.objects.create()
            qaa.pi = pi
            qaa.save()
    else:
        create_new_qaa = True

    if create_new_qaa:
        print('created new qaa and pi')
        pi = ProjectInfo.objects.create()
        qaa = QlassicAssessmentApplication.objects.create(user=request.user, pi=pi)

    # Refresh new information
    # pi.project_type = contractor.project_type
    pi.levy_number = contractor.levy_number
    pi.project_title = contractor.project_title
    pi.project_reference_number = contractor.project_reference_number
    pi.contractor_name = contractor.name_of_contractor
    pi.contractor_cidb_registration_no = contractor.contractor_registration_number
    pi.contractor_registration_grade = contractor.contractor_registration_grade
    pi.contract_value = contractor.contract_value
    pi.project_location = contractor.project_location
    pi.save()
    qaa.applicant_name = request.user.name
    qaa.role = request.user.role
    qaa.organization = request.user.organization
    qaa.address1 = request.user.address1
    qaa.address2 = request.user.address2
    qaa.city = request.user.city
    qaa.state = request.user.state
    qaa.postcode = request.user.postcode
    qaa.email = request.user.email
    qaa.hp_no = request.user.hp_no
    qaa.fax_no = request.user.fax_no
    qaa.save()

    assessment_data, created = AssessmentData.objects.get_or_create(qaa=qaa)

    form_qaa = QAACreateForm(instance=qaa)
    if request.method == 'POST':
        form_qaa = QAAApplicationForm(request.POST, instance=qaa)
        if form_qaa.is_valid():
            qaa = form_qaa.save()
            messages.info(request, 'Successfully save')
            return redirect('dashboard_application_new_2', contractor.contractor_registration_number,
                            contractor.project_reference_number)
        else:
            messages.warning(request, 'Problem with details' + form_qaa.errors.as_text())
            return redirect('dashboard_application_new', contractor.contractor_registration_number,
                            contractor.project_reference_number)

    #     if contractor.qaa_number == None:

    #         qaa = QlassicAssessmentApplication.objects.get_or_create(
    #             first_name='John',
    #             last_name='Lennon',
    #             defaults={'birthday': date(1940, 10, 9)},
    #         )
    context = {'qaa': qaa, 'form_qaa': form_qaa, 'contractor': contractor}
    return render(request, "dashboard/application/application_form_1.html", context)


@login_required(login_url="/login/")
def dashboard_application_new_2(request, contractor_registration_number, id):
    # contractor = get_object_or_404(Contractor, contractor_registration_number=contractor_registration_number, project_reference_number=id)
    contractor = Contractor.objects.filter(contractor_registration_number=contractor_registration_number,
                                           project_reference_number=id)[0]

    qaa = \
    QlassicAssessmentApplication.objects.filter(pi__contractor_cidb_registration_no=contractor_registration_number,
                                                pi__project_reference_number=id).order_by('-created_date')[0]
    pi = qaa.pi

    form_pi = ProjectInfoCreateForm(instance=pi)
    if request.method == 'POST':
        form_pi = ProjectInfoApplicationForm(request.POST, request.FILES, instance=pi)
        if form_pi.is_valid():
            pi_submit = form_pi.save()
            if pi_submit.project_type == 'GOVERNMENT':
                qaa.payment_mode = 'off'
            else:
                # qaa.payment_mode = 'on'
                qaa.payment_mode = 'off'
            qaa.save()
            messages.info(request, 'Successfully save')

            return redirect('dashboard_application_new_3', contractor.contractor_registration_number,
                            contractor.project_reference_number)
        else:
            messages.warning(request, 'Problem with details' + form_pi.errors.as_text())
            return redirect('dashboard_application_new_2', contractor.contractor_registration_number,
                            contractor.project_reference_number)

    context = {'pi': pi, 'form_pi': form_pi, 'contractor': contractor}
    return render(request, "dashboard/application/application_form_2.html", context)


@login_required(login_url="/login/")
def dashboard_application_new_3(request, contractor_registration_number, id):
    # contractor = get_object_or_404(Contractor, contractor_registration_number=contractor_registration_number, project_reference_number=id)
    contractor = Contractor.objects.filter(contractor_registration_number=contractor_registration_number,
                                           project_reference_number=id)[0]

    qaa = \
    QlassicAssessmentApplication.objects.filter(pi__contractor_cidb_registration_no=contractor_registration_number,
                                                pi__project_reference_number=id).order_by('-created_date')[0]
    pi = qaa.pi

    print(generate_qaa_number(qaa))

    sd = SupportingDocuments.objects.all().filter(qaa=qaa)
    sd_1, created = sd.get_or_create(qaa=qaa, file_name='sd_1')
    sd_2, created = sd.get_or_create(qaa=qaa, file_name='sd_2')
    sd_3, created = sd.get_or_create(qaa=qaa, file_name='sd_3')
    sd_4, created = sd.get_or_create(qaa=qaa, file_name='sd_4')
    sd_5, created = sd.get_or_create(qaa=qaa, file_name='sd_5')
    sd_6, created = sd.get_or_create(qaa=qaa, file_name='sd_6')
    sd_7, created = sd.get_or_create(qaa=qaa, file_name='sd_7')
    sd_8, created = sd.get_or_create(qaa=qaa, file_name='sd_8')
    sd_9, created = sd.get_or_create(qaa=qaa, file_name='sd_9')
    context = {
        'contractor': contractor,
        'sd_1': sd_1,
        'sd_2': sd_2,
        'sd_3': sd_3,
        'sd_4': sd_4,
        'sd_5': sd_5,
        'sd_6': sd_6,
        'sd_7': sd_7,
        'sd_8': sd_8,
        'sd_9': sd_9
    }
    if request.method == 'POST':
        form_sd = SupportingDocumentsUploadForm(request.POST, request.FILES)
        if form_sd.is_valid():
            data_sd_1 = form_sd.cleaned_data.get('sd_1')
            data_sd_2 = form_sd.cleaned_data.get('sd_2')
            data_sd_3 = form_sd.cleaned_data.get('sd_3')
            data_sd_4 = form_sd.cleaned_data.get('sd_4')
            data_sd_5 = form_sd.cleaned_data.get('sd_5')
            data_sd_6 = form_sd.cleaned_data.get('sd_6')
            data_sd_7 = form_sd.cleaned_data.get('sd_7')
            data_sd_8 = form_sd.cleaned_data.get('sd_8')
            data_sd_9 = form_sd.cleaned_data.get('sd_9')
            if data_sd_1 != None:
                sd_1.file = data_sd_1
                sd_1.save()
            if data_sd_2 != None:
                sd_2.file = data_sd_2
                sd_2.save()
            if data_sd_3 != None:
                sd_3.file = data_sd_3
                sd_3.save()
            if data_sd_4 != None:
                sd_4.file = data_sd_4
                sd_4.save()
            if data_sd_5 != None:
                sd_5.file = data_sd_5
                sd_5.save()
            if data_sd_6 != None:
                sd_6.file = data_sd_6
                sd_6.save()
            if data_sd_7 != None:
                sd_7.file = data_sd_7
                sd_7.save()
            if data_sd_8 != None:
                sd_8.file = data_sd_8
                sd_8.save()
            if data_sd_9 != None:
                sd_9.file = data_sd_9
                sd_9.save()

            # Change status to pending
            qaa.application_status = 'pending'

            # Generate QAA Number
            # if qaa.qaa_number == None or qaa.qaa_number == '':
            #     qaa_count = ProjectInfo.objects.filter(project_location=pi.project_location,qaa__building_type=qaa.building_type,project_type=pi.project_type).exclude(qaa__qaa_number='').count()
            #     qaa_number = ''
            #     new_number = False
            #     while new_number==False:
            #         qaa_count += 1
            #         print(contractor.project_type)
            #         qaa_number = get_state_code(pi.project_location) + datetime.datetime.now().strftime('%y') + ' ' + qaa.building_type + 'P' + str(qaa_count).zfill(4) + " C (" + get_sector_code(pi.project_type) + ")"
            #         check_qaa_exist = QlassicAssessmentApplication.objects.all().filter(qaa_number=qaa_number)
            #         if check_qaa_exist.count() == 0:
            #             new_number=True
            #     qaa.qaa_number = qaa_number
            if qaa.qaa_number == None or qaa.qaa_number == '':
                qaa_number = generate_qaa_number(qaa)
                qaa.qaa_number = qaa_number

            qaa.created_date = datetime.datetime.now()
            qaa.save()

            messages.info(request, 'QLASSIC Assessment Application completed')

            # Email send to User
            subject = 'QLASSIC Assessment Application are being Processed (' + qaa.qaa_number + ')'
            context = {
                'qaa': qaa,
                'user': request.user,
            }
            to = [request.user.email]
            send_email_default(subject, to, context, 'email/qaa-sent.html')

            # Email send to reviewer
            reviewers = CustomUser.objects.all().filter(
                Q(role='casc_reviewer') |
                Q(role='superadmin')
            )
            to = []
            context = {
                'qaa': qaa
            }
            for rev in reviewers:
                to.append(rev.email)
            subject = 'New QLASSIC Assessment Application to be reviewed (' + qaa.qaa_number + ')'
            send_email_default(subject, to, context, 'email/qaa-sent-reviewer.html')

            return redirect('dashboard_application_list')
        else:
            messages.warning(request, 'Problem with uploading the documents: ' + form_sd.errors.as_text())
        return redirect('dashboard_application_new_3', contractor.contractor_registration_number,
                        contractor.project_reference_number)

    return render(request, "dashboard/application/application_form_3.html", context)


def generate_qaa_number(qaa):
    # Get list of all applied project
    project_applied = QlassicAssessmentApplication.objects.all().exclude(
        Q(qaa_number='') |
        Q(qaa_number=None)
    )

    # Find project that match with current project
    current_year = datetime.datetime.now().strftime('%Y')
    fil = project_applied.filter(
        pi__created_date__year=current_year,
        pi__project_location=qaa.pi.project_location,
        building_type=qaa.building_type,
        pi__project_type=qaa.pi.project_type,
    )

    qaa_number = ''
    count = len(fil)
    new_number = False

    # Generate QAA unique number
    while new_number == False:
        count += 1
        qaa_number = get_state_code(qaa.pi.project_location) + datetime.datetime.now().strftime(
            '%y') + ' ' + qaa.building_type + 'P' + str(count).zfill(4) + " C (" + get_sector_code(
            qaa.pi.project_type) + ")"
        check_qaa_exist = project_applied.filter(qaa_number=qaa_number)
        if check_qaa_exist.count() == 0:
            new_number = True
    return qaa_number


@login_required(login_url="/login/")
def dashboard_application_info(request, id):
    if request.method == "POST":
        obj = QlassicAssessmentApplication.objects.filter(id=id).first()
        date = request.POST.get('get_date')
        datetime_object = datetime.datetime.strptime(date, '%d/%m/%Y')
        obj.proposed_date = datetime_object
        obj.save()
    mode = ''
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    supporting_documents = get_supporting_documents(qaa)
    context = {
        'role': request.user.role,
        'mode': mode,
        'qaa': qaa,
        'supporting_documents': supporting_documents,
    }

    return render(request, "dashboard/application/application_info.html", context)


@login_required(login_url="/login/")
def dashboard_application_info_assessor(request, id, assessor_mode):
    mode = ''

    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    supporting_documents = get_supporting_documents(qaa)
    context = {
        'mode': mode,
        'assessor_view': True,
        'assessor_mode': assessor_mode,
        'qaa': qaa,
        'supporting_documents': supporting_documents,
    }

    return render(request, "dashboard/application/application_info.html", context)


@login_required(login_url="/login/")
def dashboard_application_review(request, id):
    mode = 'review'

    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    form_review = QAAReviewForm(instance=qaa)

    supporting_documents = get_supporting_documents(qaa)
    context = {
        'mode': mode,
        'qaa': qaa,
        'form_review': form_review,
        'supporting_documents': supporting_documents
    }

    # Add special element that sub_component type is zero
    add_component_form(context, qaa)

    if request.method == 'POST':
        project_title = request.POST.get("project_title")
        qaa.pi.project_title = project_title
        qaa.pi.save()

        if 'reject' in request.POST or 'reject_amendment' in request.POST:
            if 'reject' in request.POST:
                qaa.application_status = 'rejected'
                messages.info(request, 'Successfully rejected the application')
            if 'reject_amendment' in request.POST:
                qaa.application_status = 'rejected_amendment'
                messages.info(request, 'Successfully rejected (with amendment) the application')

            qaa.remarks1 = request.POST['remarks1']
            qaa.reviewed_by = request.user.name
            qaa.reviewed_date = datetime.datetime.now()

            # Clear the previous verifier remarks
            qaa.remarks2 = None
            qaa.verified_by = None
            qaa.verified_date = None
            qaa.save()

            # Email send to User
            subject = 'QLASSIC Assessment Application are being rejected (' + qaa.qaa_number + ')'
            context = {
                'qaa': qaa,
                'user': request.user,
            }
            to = [request.user.email]
            send_email_default(subject, to, context, 'email/qaa-rejected.html')

            return redirect('dashboard_application_list')
        if 'accept' in request.POST:
            form_review = QAAReviewForm(request.POST, instance=qaa)
            if form_review.is_valid():

                validate_component_form(context, request, qaa)

                form_review.save()
                qaa.reviewed_by = request.user.name
                qaa.reviewed_date = datetime.datetime.now()

                qaa.remarks2 = None
                qaa.verified_by = None
                qaa.verified_date = None

                qaa.application_status = 'reviewed'
                qaa.save()

                messages.info(request, 'Successfully reviewed the application')

                # Email send to verifier
                verifiers = CustomUser.objects.all().filter(
                    Q(role='casc_verifier') |
                    Q(role='superadmin')
                )
                to = []
                context = {
                    'qaa': qaa
                }
                for ver in verifiers:
                    to.append(ver.email)
                subject = 'New QLASSIC Assessment Application to be verified (' + qaa.qaa_number + ')'
                send_email_default(subject, to, context, 'email/qaa-sent-verifier.html')

                return redirect('dashboard_application_list')
            else:
                messages.warning(request, 'Problem with reviewing the application:' + form_review.errors.as_text())
                return redirect('dashboard_application_review', qaa.id)
        if 'review_sd' in request.POST:
            status = save_reviewed_supporting_documents(request, supporting_documents)
            if status == True:
                messages.info(request, 'Successfully uploaded the reviewed document.')
            else:
                messages.warning(request, 'Problem with uploading the reviewed document.')
            return redirect('dashboard_application_review', qaa.id)

    return render(request, "dashboard/application/application_info.html", context)


@login_required(login_url="/login/")
def dashboard_application_verify(request, id):
    mode = 'verify'

    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)

    form_verify = QAAVerifyForm(instance=qaa)

    supporting_documents = get_supporting_documents(qaa)
    context = {
        'mode': mode,
        'qaa': qaa,
        'form_verify': form_verify,
        'supporting_documents': supporting_documents,
    }

    add_component_form(context, qaa)

    if request.method == 'POST':
        if 'reject' in request.POST or 'reject_amendment' in request.POST:
            if 'reject' in request.POST:
                qaa.application_status = 'rejected'
                messages.info(request, 'Successfully rejected the application')
            if 'reject_amendment' in request.POST:
                qaa.application_status = 'rejected_amendment'
                messages.info(request, 'Successfully rejected (with amendment) the application')

            qaa.remarks2 = request.POST['remarks2']
            qaa.verified_by = request.user.name
            qaa.verified_date = datetime.datetime.now()
            qaa.save()

            # Email send to User
            subject = 'QLASSIC Assessment Application are being rejected (' + qaa.qaa_number + ')'
            context = {
                'qaa': qaa,
                'user': request.user,
            }
            to = [request.user.email]
            send_email_default(subject, to, context, 'email/qaa-rejected.html')

            return redirect('dashboard_application_list')
        if 'accept' in request.POST:
            form_verify = QAAVerifyForm(request.POST, instance=qaa)
            if form_verify.is_valid():

                validate_component_form(context, request, qaa)

                form_verify.save()
                qaa.verified_by = request.user.name
                qaa.verified_date = datetime.datetime.now()
                if qaa.payment_mode == 'off':
                    qaa.application_status = 'verified'

                    # Email CASC Verifier
                    verifiers = CustomUser.objects.all().filter(
                        Q(role='casc_verifier') |
                        Q(role='superadmin')
                    )
                    to = []
                    for verifier in verifiers:
                        to.append(verifier.email)
                    subject = "Assessor Assignation - " + qaa.qaa_number
                    ctx_email = {
                        'qaa': qaa,
                    }
                    send_email_default(subject, to, ctx_email, 'email/qaa-verified.html')
                else:
                    qaa.application_status = 'need_payment'
                qaa.save()

                # Remove current suggestion
                assessors = SuggestedAssessor.objects.all().filter(qaa=qaa)
                assessors.delete()

                # Create suggested assessor based on value set by verifier and assign the assessor randomly
                sas = SuggestedAssessor.objects.all().filter(qaa=qaa)
                i = 0
                ass_list = list(Assessor.objects.all())
                random.shuffle(ass_list)
                for x in range(qaa.no_of_assessor):
                    sa = SuggestedAssessor.objects.create(qaa=qaa)
                    if i < len(ass_list):
                        print(ass_list[i])
                        sa.assessor = ass_list[i]
                        sa.assessor_no = ass_list[i].assessor_no
                        sa.save()
                    i = i + 1

                messages.info(request, 'Successfully verified the application')
                return redirect('dashboard_application_list')
            else:
                messages.warning(request, 'Problem with verifying the application:' + form_verify.errors.as_text())
                return redirect('dashboard_application_verify', qaa.id)
        if 'review_sd' in request.POST:
            status = save_reviewed_supporting_documents(request, supporting_documents)
            if status == True:
                messages.info(request, 'Successfully uploaded the reviewed document.')
            else:
                messages.warning(request, 'Problem with uploading the reviewed document.')
            return redirect('dashboard_application_verify', qaa.id)

    return render(request, "dashboard/application/application_info.html", context)


@login_required(login_url="/login/")
def dashboard_application_list(request):
    print("hello boss")
    qaas = None
    role_display_staff = [
        'superadmin',
        'casc_reviewer',
        'casc_verifier',
        'cidb_verifier',
    ]
    role_display_applicant = [
        'contractor',
        'applicant',
    ]

    # alert for none
    # print(request.user.role)
    # if request.user.role == 'none':
    #    messages.warning(request, 'WE DID IT BABYYY')

    role_type = ''
    if request.user.role in role_display_staff:
        print('if')
        role_type = 'staff'
        qaas = QlassicAssessmentApplication.objects.all().order_by('-created_date')
        print(qaas, '________qasssss::::::::')
    elif request.user.role in role_display_applicant:
        print('elif')
        role_type = 'applicant'
        qaas = QlassicAssessmentApplication.objects.all().filter(user=request.user).order_by('-created_date')
    else:
        print('else')
        messages.warning(request,
                         "Please write us a letter and email at casc@cream.my for verification purpose. Download template letter at Homepage>Publication (click CIDB's logo)")
        qaas = None

    # GET Filter
    sector = ''
    if qaas != None:
        if 'sector' in request.GET:
            sector = request.GET['sector']
            if sector != '':
                qaas = qaas.filter(pi__project_type=sector)

    context = {
        'role_type': role_type,
        'sector': sector,
        'qaas': qaas,
        'payment_history_url': get_payment_history_url(request),
    }

    if request.method == 'POST':
        if request.POST.get("project_title_child"):
            title = request.POST.get("project_title_child")
            value = request.POST.get("project_value_child")
            parent_object_id = request.POST.get("parent_object")
            qaa = get_object_or_404(ProjectInfo, id=parent_object_id)
            project, created = ProjectInfo.objects.get_or_create(parent_obj=qaa)
            if created:
                project.project_title = title
                project.value = value
                project.save()

            return redirect('dashboard_application_list')
        if 'reapply' in request.POST:
            # id = request.POST['id']
            contractor_cidb_registration_no = request.POST['contractor_cidb_registration_no']
            project_reference_number = request.POST['project_reference_number']
            subject = "That’s your subject"
            obj_email = {
                'contractor_cidb_registration_no': contractor_cidb_registration_no,
            }
            send_email_default(subject, obj_email, 'email/qaa-payment-response.html')

            # contractor = Contractor.objects.get(id=id)
            # return redirect('dashboard_application_new', contractor.id)
            return redirect('dashboard_application_new', contractor_cidb_registration_no, project_reference_number)

    return render(request, "dashboard/application/application_list.html", context)


# @login_required(login_url="/login/")
# def dashboard_application_payment(request, id):
#     mode = 'payment'
#     qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
#     response = create_transaction(request, qaa.no_of_blocks, 'QLC', 'PERMOHONAN PENILAIAN QLASSIC', qaa.qaa_number, request.user)
#     print(response)
#     proforma = response.Code

#     response_url = get_domain(request) + '/dashboard/application/payment/'+id+'/response/'

#     # Create Payment
#     payment, created = Payment.objects.get_or_create(order_id=proforma)
#     payment.user = request.user
#     payment.customer_name = request.user.name
#     payment.customer_email = request.user.email
#     payment.qaa = qaa
#     payment.currency = 'MYR'
#     payment.payment_amount = response.Amount
#     payment.save()

#     context = {
#         'title': 'Payment - QLASSIC Assessment Application',
#         'mode': mode,
#         'qaa': qaa,
#         'proforma': proforma,
#         'amount': payment.payment_amount,
#         'response': response,
#         'url': payment_gateway_url,
#         'response_url': response_url,
#     }
#     return render(request, "dashboard/application/payment.html",context)

@login_required(login_url="/login/")
def dashboard_application_payment(request, id):
    mode = 'payment'
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    response = create_transaction(request, qaa.no_of_blocks, 'QLC', 'PERMOHONAN PENILAIAN QLASSIC', qaa.qaa_number,
                                  request.user)
    print(response)
    proforma = response.Code

    response_url = get_domain(request) + '/dashboard/application/payment/' + id + '/response/'

    # Create Payment
    payment, created = Payment.objects.get_or_create(order_id=proforma)
    payment.user = request.user
    payment.customer_name = request.user.name
    payment.customer_email = request.user.email
    payment.qaa = qaa
    payment.currency = 'MYR'
    payment.payment_amount = response.Amount
    payment.save()

    postdata = {
        'ClientReturnURL': response_url,
        'IcOrRoc': request.user.code_id,
        'OrderID': proforma,
        'Currency': "MYR",
        'TransactionType': "SALE",
        'ClientRef0': "",
        'ClientRef1': "",
        'ClientRef2': "",
        'ClientRef3': "",
        'ClientRef4': "",
        'Amount': payment.payment_amount,
        'CustomerName': request.user.name,
        'CustomerEmail': request.user.email,
        'CustomerPhoneNo': request.user.hp_no,
    }

    return requests.post(payment_gateway_url, data=postdata).json()


@csrf_exempt
def dashboard_application_payment_response(request, id):
    mode = 'payment_response'
    payment = None
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    if request.method == 'POST':
        payment = payment_response_process(request)
        if payment != None:
            qaa.payment_status = payment.payment_status
            qaa.save()
            if payment.payment_status == 1:
                qaa.application_status = 'verified'
                qaa.save()
                messages.info(request, 'Payment is successful. Your application will be reviewed soon.')

                # Email
                reviewers = CustomUser.objects.all().filter(role='casc_reviewer')
                to = []
                for reviewer in reviewers:
                    to.append(reviewer.email)
                subject = "New Transaction for QLASSIC Assessment Application - " + qaa.qaa_number
                ctx_email = {
                    'qaa': qaa,
                    'payment': payment,
                }
                send_email_default(subject, to, ctx_email, 'email/qaa-payment-response.html')

                # Email CASC Verifier
                verifiers = CustomUser.objects.all().filter(
                    Q(role='casc_verifier') |
                    Q(role='superadmin')
                )
                to = []
                for verifier in verifiers:
                    to.append(verifier.email)
                subject = "Assessor Assignation - " + qaa.qaa_number
                ctx_email = {
                    'qaa': qaa,
                }
                send_email_default(subject, to, ctx_email, 'email/qaa-verified.html')
            elif payment.payment_status == 2:
                messages.info(request, payment.status_description)
                qaa.status = 'verified'
                qaa.save()
            else:
                messages.warning(request, payment.status_description)
        else:
            messages.warning(request,
                             'Problem with processing the transaction. Please contact with our staff to verify the transaction')
    receipt_url = None
    if payment != None:
        receipt_url = get_receipt_url + payment.order_id

    context = {
        'title': 'Payment Response - QLASSIC Assessment Application',
        'mode': mode,
        'training': qaa,
        'receipt_url': receipt_url,
        'payment': payment,
    }
    return render(request, "dashboard/application/payment.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'casc_verifier', 'assessor'])
def dashboard_application_assessor_list(request):
    mode = 'list_all'
    context = {}
    if request.user.role == 'superadmin' or request.user.role == 'casc_verifier':
        mode = 'list_all'

    elif request.user.is_assessor:
        mode = 'list_own'
    else:
        mode = 'list_all'

    if mode == 'list_own':
        suggested_assessors = SuggestedAssessor.objects.all().filter(assessor__user=request.user).exclude(
            acception=None)
        context = {
            'suggested_assessors': suggested_assessors,
            'mode': mode,
        }
    else:
        qaas = QlassicAssessmentApplication.objects.all().filter(
            Q(application_status='verified') |
            Q(application_status='assessor_assign')
        )
        suggested_assessors = SuggestedAssessor.objects.all()
        context = {
            'qaas': qaas,
            'suggested_assessors': suggested_assessors,
            'mode': mode,
        }
    return render(request, "dashboard/application/assessor_list.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'casc_verifier', 'assessor'])
def dashboard_application_assessor_list_all(request):
    mode = 'list_all'
    qaas = QlassicAssessmentApplication.objects.all()
    # .filter(
    #     Q(application_status='verified')|
    #     Q(application_status='assessor_assign')
    # )
    print(qaas, 'test')
    suggested_assessors = SuggestedAssessor.objects.all()
    print(suggested_assessors, 'ok')
    context = {
        'qaas': qaas.order_by('-modified_date'),
        'suggested_assessors': suggested_assessors,
        'mode': mode,
    }
    return render(request, "dashboard/application/assessor_list.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'casc_verifier', 'assessor'])
def dashboard_application_assessor_list_own(request):
    mode = 'list_own'
    suggested_assessors = SuggestedAssessor.objects.all().filter(assessor__user=request.user).exclude(acception=None)
    context = {
        'suggested_assessors': suggested_assessors,
        'mode': mode,
    }

    return render(request, "dashboard/application/assessor_list.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'casc_verifier'])
def dashboard_application_assessor_assign(request, id):
    mode = 'assign_assessor'

    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    pi = qaa.pi
    suggested_assessors = SuggestedAssessor.objects.all().filter(qaa=qaa)

    supporting_documents = get_supporting_documents(qaa)

    # date range
    if qaa.no_of_days > 1:
        period = qaa.no_of_days - 1
        end_date = qaa.assessment_date + datetime.timedelta(hours=period * 24)
        assessment_date = f"{qaa.assessment_date} hingga {end_date}"
    else:
        assessment_date = qaa.assessment_date

    context = {
        'suggested_assessors': suggested_assessors,
        'mode': mode,
        'qaa': qaa,
        'supporting_documents': supporting_documents,
        'assessment_date': assessment_date,
    }

    if request.method == 'POST':
        assessment_data, created = AssessmentData.objects.get_or_create(qaa=qaa)
        assessment_data.user = request.user
        assessment_data.save()

        print("suggested assessors2", suggested_assessors)

        # Email Assigned Assessor
        to = []

        for sa in suggested_assessors:
            # check if assessor changed or not

            # previous logic
            # if acceptance == none -> pending
            # else pass

            # new logic
            # if acceptance == prev_acceptance and is not None

            if sa.acception == 'accept' or sa.acception == 'pending':
                pass
            else:
                sa.acception = 'pending'
                sa.save()

            to.append(sa.assessor.user.email)

            # developer email test 
        subject = "Assessor Assignation - " + qaa.qaa_number
        ctx_email = {
            'qaa': qaa,
        }
        send_email_default(subject, to, ctx_email, 'email/qaa-assessor-assigned.html')

        qaa.save()
        messages.info(request, 'Successfully assigned the assessors.')
        return redirect('dashboard_application_assessor_list_all')
    return render(request, "dashboard/application/application_info.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'casc_verifier'])
def dashboard_application_assessor_reassign(request, id):
    mode = 'assign_assessor'

    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    pi = qaa.pi
    suggested_assessors = SuggestedAssessor.objects.all().filter(qaa=qaa)
    for sa in suggested_assessors:
        print(sa.acception)

    supporting_documents = get_supporting_documents(qaa)

    if qaa.no_of_days > 1:
        period = qaa.no_of_days - 1
        end_date = qaa.assessment_date + datetime.timedelta(hours=period * 24)
        assessment_date = f"{qaa.assessment_date} - {end_date}"
    else:
        assessment_date = qaa.assessment_date

    context = {
        'suggested_assessors': suggested_assessors,
        'mode': mode,
        'qaa': qaa,
        'supporting_documents': supporting_documents,
        'assessment_date': assessment_date,
    }

    if request.method == 'POST':

        assessment_data, created = AssessmentData.objects.get_or_create(qaa=qaa)
        assessment_data.user = request.user
        assessment_data.save()

        # Email Assigned Assessor
        to = []
        for sa in suggested_assessors:
            if sa.acception == 'accept' or sa.acception == 'pending':
                pass
            else:

                to.append(sa.assessor.user.email)
                sa.acception = 'pending'
                sa.save()

        print("receiver", to)
        subject = "Assessor Assignation - " + qaa.qaa_number
        ctx_email = {
            'qaa': qaa,
        }
        send_email_default(subject, to, ctx_email, 'email/qaa-assessor-assigned.html')

        qaa.save()
        messages.info(request, 'Successfully assigned the assessors.')
        return redirect('dashboard_application_assessor_list_all')
    return render(request, "dashboard/application/application_info_reassign.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'assessor'])
def dashboard_application_assessor_approve(request, id):
    mode = 'verify_assessor'
    suggested_assessor = get_object_or_404(SuggestedAssessor, id=id)
    assessor = suggested_assessor.assessor
    if assessor.user != request.user:
        raise Http404

    qaa = suggested_assessor.qaa
    assessment_data, created = AssessmentData.objects.get_or_create(qaa=qaa)

    supporting_documents = get_supporting_documents(qaa)
    context = {
        'suggested_assessor': suggested_assessor,
        'mode': mode,
        'assessor_view': True,
        'qaa': qaa,
        'supporting_documents': supporting_documents,
    }
    if request.method == 'POST':
        if 'reject' in request.POST:
            suggested_assessor.acception = 'reject'
            suggested_assessor.save()
            suggested_assessor.remarks = request.POST['remarks']
            messages.info(request, 'Successfully reject the assessor assignation.')
        if 'accept' in request.POST:
            suggested_assessor.acception = 'accept'
            suggested_assessor.remarks = request.POST['remarks']
            suggested_assessor.save()

            AssignedAssessor.objects.get_or_create(
                ad=assessment_data,
                assessor=suggested_assessor.assessor,
                assessor_number=suggested_assessor.assessor_no,
                name=suggested_assessor.assessor.user.name,
                role_in_assessment='assessor',
            )

            # Check if suggested assessor is accepted
            all_suggested_assessor = SuggestedAssessor.objects.all().filter(qaa=qaa).exclude(assessor=None)
            complete = True
            for all in all_suggested_assessor:
                if all.acception != 'accept':
                    complete = False
                    break
            if complete == True:
                qaa.application_status = 'assessor_assign'

                # send email goes here manega
                subject = 'QLASSIC Site Assessment (' + qaa.qaa_number + ')'
                context = {
                    'qaa': qaa,
                    'assessment_data': assessment_data
                }
                to = [qaa.user.email]
                send_email_default(subject, to, context, 'email/notify_contractor_after_assigned.html')

                qaa.save()

                # Assign Lead Assessor
                highest = -1
                lead_assessor = None
                for all in all_suggested_assessor:
                    temp = AssignedAssessor.objects.all().filter(assessor=all.assessor)
                    count = len(temp)
                    print('count:' + str(count))
                    if count > highest:
                        highest = count
                        lead_assessor = all.assessor
                lead_assigned_assessor = AssignedAssessor.objects.all().filter(assessor=lead_assessor,
                                                                               ad=assessment_data).first()
                lead_assigned_assessor.role_in_assessment = 'lead_assessor'
                lead_assigned_assessor.save()

            messages.info(request, 'Successfully accept the assessor assignation.')
        return redirect('dashboard_application_assessor_list_own')
    return render(request, "dashboard/application/application_info.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'casc_verifier'])
def dashboard_application_assessor_change(request, id):
    current = get_object_or_404(SuggestedAssessor, id=id)
    assessors = Assessor.objects.all()
    if request.method == 'POST':
        assessor_id = request.POST['assessor_id']
        assessor = Assessor.objects.get(id=assessor_id)
        current.assessor = assessor
        current.assessor_no = assessor.assessor_no
        current.acception = None
        current.save()
        messages.info(request, 'Successfully changed the Suggested Assessor')
        return redirect('dashboard_application_assessor_assign', current.qaa.id)
    context = {
        'current': current,
        'assessors': assessors
    }
    return render(request, "dashboard/application/assessor_change.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'casc_verifier'])
def dashboard_application_assessor_rechange(request, id):
    current = get_object_or_404(SuggestedAssessor, id=id)
    qaa = current.qaa
    prevAssessor = current.assessor
    assessors = Assessor.objects.all()
    if request.method == 'POST':

        assessor_id = request.POST['assessor_id']
        assessor = Assessor.objects.get(id=assessor_id)
        current.assessor = assessor
        current.assessor_no = assessor.assessor_no
        current.acception = None
        current.save()

        # delete the previous
        ad = AssessmentData.objects.get(qaa=qaa)
        prev_assessors = AssignedAssessor.objects.all().filter(ad_id=ad.id)
        print("before", prev_assessors)

        prev_assessor = []
        for i in prev_assessors:
            if i.assessor == prevAssessor:
                i.delete()

        prev_assessors = AssignedAssessor.objects.all().filter(ad_id=ad.id)
        print("after", prev_assessors)

        messages.info(request, 'Successfully changed the Suggested Assessor')
        return redirect('dashboard_application_assessor_reassign', current.qaa.id)
    context = {
        'current': current,
        'assessors': assessors
    }
    return render(request, "dashboard/application/assessor_change.html", context)


from decimal import Decimal


## Functions
def get_supporting_documents(qaa):
    index = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    supporting_documents = []
    sds = SupportingDocuments.objects.all().filter(qaa=qaa)
    for i in index:
        name = "sd_" + i
        sd, created = sds.get_or_create(qaa=qaa, file_name=name)
        supporting_documents.append({
            'no': i,
            'name': name,
            'title': get_qaa_sd_name(name),
            'sd': sd
        })

    return supporting_documents


## Will return form valid status (True or False)
def save_supporting_documents(request, supporting_documents):
    form_sd = SupportingDocumentsUploadForm(request.POST, request.FILES)
    if form_sd.is_valid():
        for sd in supporting_documents:
            data_sd = form_sd.cleaned_data.get(sd['name'])
            if data_sd != None:
                supporting_documents.sd.file = data_sd
                supporting_documents.sd.save()
        return True
    else:
        return False


def save_reviewed_supporting_documents(request, supporting_documents):
    form_sd = SupportingDocumentsUploadForm(request.POST, request.FILES)
    if form_sd.is_valid():
        for sd in supporting_documents:
            name = sd['name']
            data_sd = form_sd.cleaned_data.get(sd['name'])
            print(name + str(data_sd))
            if data_sd != None:
                sd['sd'].reviewed_file = data_sd
                sd['sd'].save()
        return True
    else:
        return False


def add_component_form(context, qaa):
    component_form = []

    sub_components = SubComponent.objects.all().filter(type=0)
    element_results = ElementResult.objects.all().filter(qaa=qaa)
    for sub_component in sub_components:
        elements = Element.objects.all().filter(sub_component=sub_component)
        dict_sub_element = {
            'name': sub_component.name,
            'elements': []
        }
        for element in elements:

            form_element = {
                'name': element.name,
                'id': 'sub_component_id_' + str(element.id),
                'code': element.code_id,
                'no_of_check': element.no_of_check,
                'score': element.weightage
            }
            for result in element_results:
                if form_element['code'] == result.element_code:
                    if result.total_check > 0:
                        form_element['checked'] = True
                    break
            dict_sub_element['elements'].append(form_element)
        component_form.append(dict_sub_element)

    if len(component_form) > 0:
        context['component_form'] = component_form


def validate_component_form(context, request, qaa):
    for component in context['component_form']:
        for element in component['elements']:
            code = element['code']
            form_name = str(element['id'])
            form = request.POST.get(form_name, '')
            # element_id = form_name.replace('sub_component_id_','')
            element_result, created = ElementResult.objects.get_or_create(qaa=qaa, element_code=code)
            if form != 'on':
                element_result.delete()
            else:
                no_of_check = element['no_of_check']
                element_result.element_name = element['name']
                element_result.result = '[\'Yes\']'
                element_result.total_compliance = no_of_check
                element_result.total_check = no_of_check
                element_result.save()


def get_qaa_result(qaa):
    components = Component.objects.all().order_by('created_date')
    element_components = Element.objects.all().filter(category_weightage=True).order_by('created_date')
    sub_components = SubComponent.objects.all().filter().order_by('created_date')
    elements = Element.objects.all().filter(category_weightage=False).order_by('created_date')
    wcf = WorkCompletionForm.objects.all().filter(qaa=qaa).order_by('-created_date').first()
    # defect_groups = DefectGroup.objects.all().order_by('-created_date')
    sync_results = SyncResult.objects.all().filter(qaa=qaa, sync_complete=False)
    sync_results.delete()

    result = {}
    index_c = 'A'
    result['building_type'] = qaa.building_type
    result['components'] = []

    total_sample = 0

    ## Component
    for component in components:
        index_sc = 1
        result_c = {}
        result_c['no'] = index_c
        result_c['name'] = component.name
        result_c['type'] = component.type
        if qaa.building_type == 'A':
            result_c['weightage'] = component.weightage_a
        if qaa.building_type == 'B':
            result_c['weightage'] = component.weightage_b
        if qaa.building_type == 'C':
            result_c['weightage'] = component.weightage_c
        if qaa.building_type == 'D':
            result_c['weightage'] = component.weightage_d
        result_c['subcomponents'] = []

        # To check if need to remove from weightage
        component_total_check = 0
        component_total_compliance = 0

        ## Sub Component
        for sub_component in sub_components:
            if sub_component.component == component:
                index_e = 1
                result_sc = {}
                result_sc['no'] = index_sc
                result_sc['name'] = sub_component.name
                result_sc['type'] = sub_component.type
                result_sc['weightage'] = sub_component.get_total_weightage()
                result_sc['elements'] = []

                ## Element
                for element in elements:
                    if element.sub_component == sub_component:
                        result_e = {}
                        result_e['no'] = str(index_sc) + "." + str(index_e)
                        result_e['name'] = element.name
                        result_e['weightage'] = element.weightage

                        # Calculate Result
                        number_of_compliance = 0
                        number_of_check = 0

                        element_results = ElementResult.objects.all().filter(
                            Q(qaa=qaa, element_code=element.id) |
                            Q(qaa=qaa, element_code=element.code_id)
                        )

                        # check rendering to pdf ok or not
                        # element_results = ElementResult.objects.all()[0:3]

                        for element_result in element_results:
                            number_of_compliance += element_result.total_compliance
                            component_total_compliance += element_result.total_compliance

                            number_of_check += element_result.total_check
                            component_total_check += element_result.total_check

                        result_e['total_compliance'] = number_of_compliance
                        result_e['total_check'] = number_of_check

                        result_sc['elements'].append(result_e)
                        index_e += 1
                result_c['subcomponents'].append(result_sc)
                index_sc += 1

        result_c['total_compliance'] = component_total_compliance
        result_c['total_check'] = component_total_check
        result['components'].append(result_c)
        index_c = chr(ord(index_c) + 1)

    ## Element Component
    for element_component in element_components:
        index_sc = 1
        result_c = {}
        result_c['no'] = index_c
        result_c['name'] = element_component.name
        result_c['type'] = 3

        if qaa.building_type == 'A':
            result_c['weightage'] = element_component.weightage_a
        if qaa.building_type == 'B':
            result_c['weightage'] = element_component.weightage_b
        if qaa.building_type == 'C':
            result_c['weightage'] = element_component.weightage_c
        if qaa.building_type == 'D':
            result_c['weightage'] = element_component.weightage_d

        number_of_compliance = 0
        number_of_check = 0
        element_results = ElementResult.objects.all().filter(
            Q(qaa=qaa, element_code=element_component.id) |
            Q(qaa=qaa, element_code=element_component.code_id)
        )
        for element_result in element_results:
            number_of_compliance += element_result.total_compliance

            number_of_check += element_result.total_check

        result_c['total_compliance'] = number_of_compliance
        result_c['total_check'] = number_of_check
        result['components'].append(result_c)
        index_c = chr(ord(index_c) + 1)

    #### Calculate Result

    # Step 1. Recalculate Area Weightage
    total_area_weightage = 0
    for component in result['components']:
        if int(component['total_check']) > 0:
            total_area_weightage += Decimal(component['weightage'])
    for component in result['components']:
        if int(component['total_check']) > 0:
            component['actual_weightage'] = Decimal(component['weightage']) / total_area_weightage * 100
        else:
            component['actual_weightage'] = 0

    # Step 2. Recalculate Element Weightage
    for component in result['components']:
        if component['type'] == 1:
            total_element_weightage = 0
            if 'subcomponents' in component:
                for subcomponent in component['subcomponents']:
                    total_sub_component_weightage = 0
                    if 'elements' in subcomponent:
                        for element in subcomponent['elements']:
                            if int(element['total_check'] > 0):
                                total_element_weightage += Decimal(element['weightage'])
                                total_sub_component_weightage += Decimal(element['weightage'])
                    subcomponent['actual_weightage'] = total_sub_component_weightage

                # component['actual_weightage'] = total_element_weightage
                print(subcomponent['actual_weightage'])
                for subcomponent in component['subcomponents']:
                    if 'elements' in subcomponent:
                        for element in subcomponent['elements']:
                            if int(element['total_check']) > 0:
                                if Decimal(subcomponent['actual_weightage']) > 0:
                                    # element['actual_weightage'] = element['weightage'] / Decimal(subcomponent['actual_weightage']) * 100
                                    element['actual_weightage'] = element['weightage'] / Decimal(
                                        total_element_weightage) * 100
                                else:
                                    element['actual_weightage'] = 0
                            else:
                                element['actual_weightage'] = 0

    # Step 3: Calculate Score
    # for component in result['component']
    score = {}
    score['scope'] = []
    count_scope = 0
    score['components'] = []
    total_score = 0

    for component in result['components']:
        score_c = {}
        score_c['no'] = component['no']
        score_c['name'] = component['name']
        score_c['total_weightage'] = component['actual_weightage']
        score_c['subcomponents'] = []

        if component['type'] == 2 or component['type'] == 3:
            if component['total_check'] != 0:
                score_c['score'] = float(component['total_compliance']) / float(component['total_check']) * float(
                    component['actual_weightage'])
            else:
                score_c['score'] = 0
            score['components'].append(score_c)

        if component['type'] == 1:
            total_score_sub_component = 0
            score_sc_array = []
            if 'subcomponents' in component:
                for subcomponent in component['subcomponents']:
                    score_sc = {}
                    score_sc['no'] = subcomponent['no']
                    score_sc['name'] = subcomponent['name']
                    score_sc['total_weightage'] = subcomponent['actual_weightage']
                    score_sc['elements'] = []
                    # if subcomponent['type'] == 0:
                    #     total_score_element = 0
                    #     if 'elements' in subcomponent:
                    #         for element in subcomponent['elements']:
                    #             if element['total_check'] != 0:
                    #                 element_score = float(element['total_compliance']) / float(element['total_check']) * float(element['actual_weightage'])
                    #                 total_score_element += element_score
                    #     score_sc['score'] = 0
                    # score_sc_array.append(score_sc)
                    if subcomponent['type'] == 3 or subcomponent['type'] == 2 or subcomponent['type'] == 0:
                        if 'elements' in subcomponent:
                            for element in subcomponent['elements']:
                                score_e = {}
                                score_e['no'] = element['no']
                                score_e['name'] = element['name']
                                score_e['total_weightage'] = element['actual_weightage']

                                if element['total_check'] != 0:
                                    element_score = float(element['total_compliance']) / float(
                                        element['total_check']) * float(element['actual_weightage'])
                                    score_e['score'] = element_score
                                    total_score_sub_component += element_score
                                else:
                                    score_e['score'] = 0
                                score_sc['elements'].append(score_e)
                                # score_sc_array.append(score_sc)
                    score_c['subcomponents'].append(score_sc)
            # print(total_score_sub_component)
            score_c['score'] = total_score_sub_component * float(component['actual_weightage']) / 100
            score['components'].append(score_c)
            for arr in score_sc_array:
                score['components'].append(arr)

        if score_c['total_weightage'] > 0:
            count_scope += 1
            score['scope'].append(str(count_scope) + '. ' + component['name'])
            # save scope
            scope = Scope.objects.create(
                qaa=qaa,
                scope=component['name']
            )

        total_score += score_c['score']
    score['score'] = total_score

    # Corrective Maintenance Item 1

    # score['sample'] = SampleResult.objects.all().filter(qaa=qaa).count()
    score['sample'] = AssessmentData.objects.filter(qaa=qaa)[0].number_of_sample
    score['weather'] = wcf.weather

    # Rounding
    # Item 2 - fix rounding
    for component in score['components']:
        # component['score'] = round(component['score'],2)
        component['score'] = '{:.2f}'.format(component['score'])

        # component['total_weightage'] = round(component['total_weightage'],2)
        component['total_weightage'] = '{:.2f}'.format(component['total_weightage'])

        for subcomponent in component['subcomponents']:
            subcomponent['total_weightage'] = round(subcomponent['total_weightage'], 2)
            # subcomponent['total_weightage'] = '{:.2f}'.format(component['total_weightage'])

            for element in subcomponent['elements']:
                element['score'] = '{:.2f}'.format(element['score'])
                element['total_weightage'] = '{:.2f}'.format(element['total_weightage'])

                # element['score'] = round(element['score'],2)
                # element['total_weightage'] = round(element['total_weightage'],2)

    print("score", score)

    return score


def get_qlassic_score(qaa):
    print("QLASSIC SCORE")
    if qaa.qlassic_score == None:
        score_obj = get_qaa_result(qaa)
        score = score_obj['score']
        qaa.qlassic_score = score
        print("SCORE", qaa.qlassic_score)
        qaa.save()
    if qaa.casc_qlassic_score != None:
        return qaa.casc_qlassic_score
    else:
        return qaa.qlassic_score


def generate_qlassic_score(qaa):
    print("QLASSIC SCORE GENERATED")
    score_obj = get_qaa_result(qaa)
    score = score_obj['score']
    qaa.qlassic_score = score
    qaa.save()


## AJAX
@login_required(login_url="/login/")
def ajax_api_application_payment_request(request):
    if request.method == 'POST':
        id = request.POST['id']
        qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
        response = create_transaction(request, qaa.no_of_blocks, 'QLC', 'PERMOHONAN PENILAIAN QLASSIC', qaa.qaa_number,
                                      request.user)
        proforma = response.Code

        payment, created = Payment.objects.get_or_create(order_id=proforma)
        if created == False:
            if payment.payment_amount != response.Amount:
                cancel_proforma(proforma)
                response = create_transaction(request, qaa.no_of_blocks, 'QLC', 'PERMOHONAN PENILAIAN QLASSIC',
                                              qaa.qaa_number, request.user)
                proforma = response.Code
                payment, created = Payment.objects.get_or_create(order_id=proforma)

        # Create Payment
        payment.user = request.user
        payment.customer_name = request.user.name
        payment.customer_email = request.user.email
        payment.qaa = qaa
        payment.currency = 'MYR'
        payment.payment_amount = response.Amount
        payment.save()

        result = response.TransactionResult
        error = response.ErrorMessage
        response_url = get_domain(request) + '/dashboard/application/payment/' + id + '/response/'
        print(response)
        postdata = {
            'payment_gateway_url': payment_gateway_url,
            'ClientReturnURL': response_url,
            'IcOrRoc': request.user.code_id,
            'OrderID': proforma,
            'Currency': "MYR",
            'TransactionType': "SALE",
            'ClientRef0': "",
            'ClientRef1': "",
            'ClientRef2': "",
            'ClientRef3': "",
            'ClientRef4': "",
            'Amount': payment.payment_amount,
            'CustomerName': request.user.name,
            'CustomerEmail': request.user.email,
            'CustomerPhoneNo': request.user.hp_no,
            'result': result,
            'error': error,
        }

        return JsonResponse(postdata)
    else:
        return JsonResponse({})


def update_title(request, id):
    if request.method == "POST":
        doc_obj = Contractor.objects.filter(id=id).first()
        print(doc_obj, 'hello')
        name = request.POST.get('title')
        doc_obj.project_title = name
        doc_obj.save()
        return redirect('dashboard_application_project')

    return render(request, "dashboard/application/project_list.html")


def submitfeedbackview(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        comment = request.POST['comment']
        obj = SubmitFeedback.objects.create(user=request.user, name=name, email=email, comment=comment)
        obj.save()
        messages.info(request, 'Feedback Submit successfully')
        return render(request, 'Get_feedback.html')
    else:
        return render(request, 'Get_feedback.html')


def addproject(request):
    return render(request, "dashboard/application/project_list.html")


class AddProjectCreateView(CreateView):
    form_class = AddProjectForm
    template_name = "dashboard/application/project_list.html"
    model = Contractor

    def form_valid(self, form):
        form.save()
        print(form.errors)
        messages.success(self.request, "Program Category Added Successfully")
        self.object = form.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard_application_project')


def excel_view(request):
    # Create a HttpResponse object and set its content_type header value to Microsoft excel.
    response = HttpResponse(content_type='application/vnd.ms-excel')
    # Set HTTP response Content-Disposition header value. Tell web server client the attached file name is students.xls.
    from time import gmtime, strftime
    dtnow = str(strftime("%Y-%m-%d", gmtime()))
    assessment_data = AssessmentData.objects.all()
    print(assessment_data, 'assessment_data')
    response['Content-Disposition'] = 'attachment;filename=%s' % 'assesment' + 'data' + '_' + '.xls'

    # Create a new Workbook file.
    work_book = xlwt.Workbook()
    # Create a new worksheet in the above workbook.
    work_sheet = work_book.add_sheet('Assesment Data')

    # This style will be applied to worksheet head row.
    style_head_row = xlwt.easyxf("""    
 
    font:
      name Arial,
      colour_index white,
      bold on,
      height 0xA0;
    pattern:
      pattern solid,
      fore-colour 0x19;
    """
                                 )
    # Define worksheet data row style.
    style_data_row = xlwt.easyxf("""
    align:
      wrap on,
      vert center,
      horiz left;
    font:
      name Arial,
      bold off,
      height 0xA0;
    borders:
      left THIN,
      right THIN,
      top THIN,
      bottom THIN;
    """
                                 )

    # Set data row date string format.
    style_data_row.num_format_str = 'M/D/YY'
    # Define a green color style.
    style_green = xlwt.easyxf(" pattern: fore-colour 0x11, pattern solid;")
    # Define a red color style.
    style_red = xlwt.easyxf(" pattern: fore-colour 0x0A, pattern solid;")
    # Generate worksheet head row data.
    work_sheet.write(0, 0, 'User', style_head_row)
    work_sheet.write(0, 1, 'Block name', style_head_row)
    work_sheet.write(0, 2, 'Unit Name', style_head_row)
    # work_sheet.write(0, 7, 'Num', style_head_row)

    work_sheet.write(0, 3, 'Number of sampling done:', style_head_row)
    work_sheet.write(0, 4, 'Number of principles samples:', style_head_row)
    work_sheet.write(0, 5, 'Number of services samples:', style_head_row)
    work_sheet.write(0, 6, 'Number of circulation samples:', style_head_row)
    work_sheet.write(0, 7, 'Number of  samples:', style_head_row)
    work_sheet.write(0, 8, 'Ptotal:', style_head_row)
    work_sheet.write(0, 9, 'stotal:', style_head_row)
    work_sheet.write(0, 10, 'ctotal:', style_head_row)

    # Generate worksheet data row data.
    row = 1
    for data in AssessmentData.objects.all():
        work_sheet.write(row, 0, data.user.email)
        work_sheet.write(row, 1, data.block)
        work_sheet.write(row, 2, data.unit)
        work_sheet.write(row, 3, data.count_sampling_done)
        work_sheet.write(row, 4, data.count_principle)
        work_sheet.write(row, 5, data.count_services)
        work_sheet.write(row, 6, data.count_circulation)
        work_sheet.write(row, 7, data.number_of_sample)
        work_sheet.write(row, 8, data.ptotal)
        work_sheet.write(row, 9, data.stotal)
        work_sheet.write(row, 10, data.ctotal)

        row = row + 1

    output = BytesIO()
    # Save the workbook data to the above StringIO object.
    work_book.save(output)
    # Reposition to the beginning of the StringIO object.
    output.seek(0)
    # Write the StringIO object's value to HTTP response to send the excel file to the web server client.
    response.write(output.getvalue())
    return response


@login_required
def edit_application_view(request, id):
    obj = get_object_or_404(QlassicAssessmentApplication, id=id)

    form = EditApplicationForm(request.POST or None, instance=obj)
    context = {'form': form}

    if form.is_valid():
        obj = form.save(commit=False)

        obj.save()

        messages.success(request, "You successfully updated the Application")
        return redirect('dashboard_application_list')

    else:
        context = {'form': form,
                   'error': 'The form was not updated successfully. Please enter in a title and content'}
    return render(request, "dashboard/application/edit_application_list.html", context)


def veiw_few_assesment(request, id):
    obj = get_object_or_404(Contractor, id=id)

    form = ViewProjectForm(request.POST or None, instance=obj)
    context = {'form': form}
    return render(request, "dashboard/application/view_project_list.html", context)


from django.views.generic.list import ListView


class ListAssesmentView(ListView):
    # specify the model for list view
    template_name = "dashboard/application/few_assesment_list.html",

    def get(self, request, *args, **kwargs):
        obj = AssessmentData.objects.all()
        context = {
            'obj': obj,
        }
        return render(request, self.template_name, context)


class ExportExcel(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        response = CreateExcell().excel_view(request)
        return response

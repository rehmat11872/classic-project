# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.conf import settings
from time import time
import numpy as np
from django.http.response import JsonResponse
from assessments.views import get_qaa_result
from datetime import date, datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, Http404
from django import template
from django.contrib import messages
from django.urls import resolve
from django.db.models import Q
from django.views.generic import View

# XHTML2PDF
from app.xhtml2pdf import link_callback
from xhtml2pdf import pisa 
from django.template.loader import get_template

# Helpers
from app.helpers.letter_templates import test_letter_template
from portal.helpers import TEMPLATE_TYPE
from trainings.helpers import get_pass_fail_translation

# Forms
from assessments.forms import DefectGroupCreateForm, SubComponentCreateForm, ElementCreateForm, ComponentCreateForm, ScoreApplicationForm
from projects.forms import VerifiedContractorForm
from portal.forms import LetterTemplateCreateForm, LetterTemplateTrainingCreateForm
from trainings.forms import TrainingTypeCreateForm

# Models
from assessments.models import AssignedAssessor, DefectGroup, QlassicReporting, SubComponent, Element, ElementResult, Component, QlassicAssessmentApplication, SupportingDocuments, SampleResult, AssessmentData, SyncResult, Scope, SiteAttendance
from trainings.models import TrainingType, Training
from projects.models import ProjectInfo, VerifiedContractor
from portal.models import Announcement, Publication, LetterTemplate, UpdateInformation

# Generate Document
from core.helpers import translate_malay_date, standard_date, generate_and_save_qr
from app.helpers.letter_templates import generate_document, generate_document_file

# Decorators
from authentication.decorators import allowed_users

# SOAP
from api.soap.get_contractor import verify_contractor

import json

### Landing Page ###
# @login_required(login_url="/login/")
def index(request):
    if request.user.is_authenticated:
        main_logo = UpdateInformation.objects.filter(user=request.user).first()
        announcements = Announcement.objects.all()
        publications = Publication.objects.all()
        context = {'announcements':announcements,'publications':publications, 'main_logo': main_logo}
        return render(request, "index.html", context)
    else:    
        announcements = Announcement.objects.all()
        publications = Publication.objects.all()
        context = {'announcements':announcements,'publications':publications,}
    return render(request, "index.html", context)

def assessment(request):
    return render(request, "assessment.html")

def training(request):
    trainings = Training.objects.all().filter(review_status='accepted',publish=True)
    context = {'trainings':trainings}
    return render(request, "training.html", context)

def contact(request):
    return render(request, "contact.html")

def announcement(request, id):
    content = get_object_or_404(Announcement, id=id)
    mode = 'announcement'
    context = {
        'content':content,
        'mode':mode,
    }
    return render(request, "detail.html", context)

def publication(request, id):
    content = get_object_or_404(Publication, id=id)
    mode = 'publication'
    context = {
        'content':content,
        'mode':mode,
    }
    return render(request, "detail.html", context)

### Admin - Reporting & Certification Module ###
@login_required(login_url="/login/")
def dashboard_report_list(request):
    projects = QlassicAssessmentApplication.objects.all().filter(
        Q(application_status='completed')|
        Q(application_status='approved')
    )

    context = {
        'projects':projects,
    }

    # method to generate report
    if request.method == 'POST':
        qaa_id = request.POST['id']
        qaa = get_object_or_404(QlassicAssessmentApplication, id=qaa_id)
        if 'qlassic_score_letter' in request.POST:
            report = assessment_report_generate(request, 'qlassic_score_letter', qaa)
            if qaa.doc_qlassic_score_letter_status == 'pending':
                qaa.doc_qlassic_score_letter_status = 'generated'
            qaa.save()
            messages.info(request,'Succesfully generated the Score Letter.')
        if 'qlassic_report' in request.POST:
            report = assessment_report_generate(request, 'qlassic_report', qaa)
            if qaa.doc_qlassic_report_status == 'pending':
                qaa.doc_qlassic_report_status = 'generated'
            qaa.save()
            messages.info(request,'Succesfully generated the QLASSIC Report.')
        if 'qlassic_certificate' in request.POST:
            report = assessment_report_generate(request, 'qlassic_certificate', qaa)
            if qaa.doc_qlassic_certificate_status == 'pending':
                qaa.doc_qlassic_certificate_status = 'generated'
            qaa.save()
            messages.info(request,'Succesfully generated the QLASSIC Certificate.')
        return redirect('dashboard_report_list')
    return render(request, "dashboard/reporting/report_list.html", context)

@login_required(login_url="/login/")
def dashboard_qlassic_report_view(request, report_type, id):
    print("button orange")
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    report, created = QlassicReporting.objects.get_or_create(qaa=qaa,report_type=report_type)
    mode = 'view'
    context = {
        'qaa':qaa,
        'report_type':report_type,
        'mode':mode,
        'report':report,
    }
    return render(request, "dashboard/reporting/report_detail.html", context)

@login_required(login_url="/login/")
def dashboard_report_casc_approve(request, report_type, id):

    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    report, created = QlassicReporting.objects.get_or_create(qaa=qaa,report_type=report_type)
    mode = 'casc_approve'
    form_score = ScoreApplicationForm(instance=qaa)
    context = {
        'qaa':qaa,
        'report_type':report_type,
        'report':report,
        'form_score':form_score,
        'mode':mode,
    }
    if request.method == 'POST':
        print("request.POST", request.POST)
        if 'approve' in request.POST:
            print("goes here ya")
            if report_type == 'qlassic_score_letter':
                qaa.doc_qlassic_score_letter_status = 'casc_approved'
                messages.info(request,'Succesfully submitted the Score Letter for review.')
            if report_type == 'qlassic_report':
                qaa.doc_qlassic_report_status = 'casc_approved'
                messages.info(request,'Succesfully submitted the QLASSIC Report for review.')
            if report_type == 'qlassic_certificate':
                qaa.doc_qlassic_certificate_status = 'casc_approved'
                messages.info(request,'Succesfully submitted the QLASSIC Status for review.')
            qaa.save()
            return redirect('dashboard_report_list')
        if 'score' in request.POST:
            form_score = ScoreApplicationForm(request.POST,instance=qaa)
            if form_score.is_valid():
                form_score.save()
                report = assessment_report_generate(request, 'qlassic_score_letter', qaa)
                report = assessment_report_generate(request, 'qlassic_report', qaa)
                report = assessment_report_generate(request, 'qlassic_certificate', qaa)
                messages.info(request,'Succesfully updated the score details.')
            return redirect('dashboard_report_casc_approve', report_type, id)
    return render(request, "dashboard/reporting/report_detail.html", context)

@login_required(login_url="/login/")
def dashboard_report_review(request, report_type, id):
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    report, created = QlassicReporting.objects.get_or_create(qaa=qaa,report_type=report_type)
    mode = 'review'
    context = {
        'qaa':qaa,
        'report':report,
        'report_type':report_type,
        'mode':mode,
    }
    if request.method == 'POST':
        if 'approve' in request.POST:
            if report_type == 'qlassic_score_letter':
                qaa.doc_qlassic_score_letter_status = 'reviewed'
                messages.info(request,'Succesfully reviewed the Score Letter.')
            if report_type == 'qlassic_report':
                qaa.doc_qlassic_report_status = 'reviewed'
                messages.info(request,'Succesfully reviewed the QLASSIC Report.')
            if report_type == 'qlassic_certificate':
                qaa.doc_qlassic_certificate_status = 'reviewed'
                messages.info(request,'Succesfully reviewed the QLASSIC Status.')
            qaa.save()
        return redirect('dashboard_report_list')
    return render(request, "dashboard/reporting/report_detail.html", context)

@login_required(login_url="/login/")
def dashboard_report_verify(request, report_type, id):
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    report, created = QlassicReporting.objects.get_or_create(qaa=qaa,report_type=report_type)
    mode = 'verify'
    context = {
        'qaa':qaa,
        'report':report,
        'report_type':report_type,
        'mode':mode,
    }
    if request.method == 'POST':
        if 'approve' in request.POST:
            if report_type == 'qlassic_score_letter':
                qaa.doc_qlassic_score_letter_status = 'verified'
                messages.info(request,'Succesfully verified the Score Letter.')
            if report_type == 'qlassic_report':
                qaa.doc_qlassic_report_status = 'verified'
                messages.info(request,'Succesfully verified the QLASSIC Report.')
            if report_type == 'qlassic_certificate':
                qaa.doc_qlassic_certificate_status = 'verified'
                messages.info(request,'Succesfully verified the QLASSIC Status.')
            qaa.save()
        return redirect('dashboard_report_list')
    return render(request, "dashboard/reporting/report_detail.html", context)

@login_required(login_url="/login/")
def dashboard_report_approve(request, report_type, id):
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    report, created = QlassicReporting.objects.get_or_create(qaa=qaa,report_type=report_type)
    mode = 'approve'
    context = {
        'qaa':qaa,
        'report':report,
        'report_type':report_type,
        'mode':mode,
    }
    if request.method == 'POST':
        if 'approve' in request.POST:
            if report_type == 'qlassic_score_letter':
                qaa.doc_qlassic_score_letter_status = 'approved'
                messages.info(request,'Succesfully approved the Score Letter.')
            if report_type == 'qlassic_report':
                qaa.doc_qlassic_report_status = 'approved'
                messages.info(request,'Succesfully approved the QLASSIC Report.')
            if report_type == 'qlassic_certificate':
                qaa.doc_qlassic_certificate_status = 'approved'
                messages.info(request,'Succesfully approved the QLASSIC Status.')
            qaa.save()
        return redirect('dashboard_report_list')
    return render(request, "dashboard/reporting/report_detail.html", context)

@login_required(login_url="/login/")
def dashboard_report_submit(request, report_type, id):
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    report, created = QlassicReporting.objects.get_or_create(qaa=qaa,report_type=report_type)
    mode = 'submit'
    context = {
        'qaa':qaa,
        'report':report,
        'report_type':report_type,
        'mode':mode,
    }
    if request.method == 'POST':
        if 'approve' in request.POST:
            reporting, created = QlassicReporting.objects.get_or_create(qaa=qaa,report_type=report_type)
            title = ''
            if report_type == 'qlassic_score_letter':
                title = 'QLASSIC Score Letter'
                qaa.doc_qlassic_score_letter_status = 'submitted'
                messages.info(request,'Succesfully submitted the Score Letter via email.')
            if report_type == 'qlassic_report':
                title = 'QLASSIC Report'
                qaa.doc_qlassic_report_status = 'submitted'
                messages.info(request,'Succesfully submitted the QLASSIC Report via email.')
            if report_type == 'qlassic_certificate':
                title = 'QLASSIC Certificate'
                qaa.doc_qlassic_certificate_status = 'submitted'
                messages.info(request,'Succesfully submitted the QLASSIC Status via email.')
            
            # Email
            user = qaa.user
            to = [user.email]
            subject = "QLASSIC Assessment - " + title + ' ('+ qaa.qaa_number +')'
            attachments = [reporting.report_file]
            email_ctx = {
                'title':title,
                'qaa': qaa,
                'user': user,
            }
            send_email_with_attachment(subject, to, email_ctx, 'email/qaa-cert-submit.html', attachments)

            qaa.save()
        return redirect('dashboard_report_list')
    return render(request, "dashboard/reporting/report_detail.html", context)

# def report_view(request, report_type, id):
#     qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
#     template_path = ''
#     if report_type == 'score_letter':
#         template_path = 'pdf/score_letter.html'
#     elif report_type == 'qlassic_report':
#         template_path = 'pdf/qlassic_report.html'
#     elif report_type == 'qlassic_certificate':
#         template_path = 'pdf/qlassic_certificate.html'
#     else:
#         raise Http404
#     qr_url = request.build_absolute_uri()
#     host_url = request.scheme+'://'+request.META['HTTP_HOST'] 
#     context = {
#         'host_url': host_url,
#         'qr_url': qr_url,
#         'qaa': qaa
#     }
#     return render(request, template_path, context)

# def report_generate(request, report_type, id):
#     template_path = ''
#     if report_type == 'score_letter':
#         template_path = 'pdf/score_letter.html'
#     elif report_type == 'qlassic_report':
#         template_path = 'pdf/qlassic_report.html'
#     elif report_type == 'qlassic_certificate':
#         template_path = 'pdf/qlassic_certificate.html'
#     else:
#         raise Http404

#     qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
#     qr_url = request.build_absolute_uri()
#     host_url = request.scheme+'://'+request.META['HTTP_HOST'] 
#     context = {
#         'host_url': host_url,
#         'qr_url': qr_url,
#         'qaa': qaa
#     }
#     # Create a Django response object, and specify content_type as pdf
#     response = HttpResponse(content_type='application/pdf')
#     # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
#     response['Content-Disposition'] = 'inline; filename="report.pdf"'
#     # find the template and render it.
#     template = get_template(template_path)
#     html = template.render(context)

#     # create a pdf
#     pisa_status = pisa.CreatePDF(
#        html, dest=response, link_callback=link_callback)
#     # if error then show some funy view
#     if pisa_status.err:
#        return HttpResponse('We had some errors <pre>' + html + '</pre>')
#     return response
import absoluteuri

from assessments.views import get_qlassic_score
# def qlassic_report_generate(request, report_type, id):
#     qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
#     tmpl_ctx = ''
#     if report_type == 'qlassic_score_letter':
#         qr_path = absoluteuri.build_absolute_uri('/cert_assessment/qlassic_score_letter/'+str(qaa.id)+'/')
#         generate_and_save_qr(qr_path, qaa.qlassic_score_letter_qr_file)
#         qr_path = absoluteuri.build_absolute_uri('/cert_assessment/qlassic_report/'+str(qaa.id)+'/')
#         generate_and_save_qr(qr_path, qaa.qlassic_report_qr_file)
#         qr_path = absoluteuri.build_absolute_uri('/cert_assessment/qlassic_certificate/'+str(qaa.id)+'/')
#         generate_and_save_qr(qr_path, qaa.qlassic_certificate_qr_file)
#         tmpl_ctx = {
#             'title': qaa.pi.project_title,
#             'qaa_number': qaa.qaa_number,
#             'assessment_date': translate_malay_date(standard_date(qaa.assessment_date)),
#             'developer': qaa.pi.developer,
#             'developer_ssm_number': qaa.pi.developer_ssm_number,
#             'contractor': qaa.pi.contractor_name,
#             'cidb_number': qaa.pi.contractor_cidb_registration_no,
#             'grade': qaa.pi.contractor_registration_grade,
#             'ccd_score': str(round(qaa.ccd_point, 2)),
#             'qlassic_score': str(round(get_qlassic_score(qaa), 2)),
#         }
#     elif report_type == 'qlassic_report':
#         qaa_result = get_qaa_result(qaa)
#         tmpl_ctx = {
#             'title': qaa.pi.project_title,
#             'qaa_number': qaa.qaa_number,
#             'assessment_date': translate_malay_date(standard_date(qaa.assessment_date)),
#             'developer': qaa.pi.developer,
#             'developer_ssm_number': qaa.pi.developer_ssm_number,
#             'contractor': qaa.pi.contractor_name,
#             'cidb_number': qaa.pi.contractor_cidb_registration_no,
#             'grade': qaa.pi.contractor_registration_grade,
#             'ccd_score': str(round(qaa.ccd_point, 2)),
#             'qlassic_score': str(round(get_qlassic_score(qaa), 2)),
#             'qaa_result': qaa_result,
#         }
#     elif report_type == 'qlassic_certificate':
#         tmpl_ctx = {
#             'title': qaa.pi.project_title,
#             'qaa_number': qaa.qaa_number,
#             'assessment_date': translate_malay_date(standard_date(qaa.assessment_date)),
#             'developer': qaa.pi.developer,
#             'developer_ssm_number': qaa.pi.developer_ssm_number,
#             'contractor': qaa.pi.contractor_name,
#             'cidb_number': qaa.pi.contractor_cidb_registration_no,
#             'grade': qaa.pi.contractor_registration_grade,
#             'ccd_score': str(round(qaa.ccd_point, 2)),
#             'qlassic_score': str(round(get_qlassic_score(qaa), 2)),
#         }
#     else:
#         raise Http404
#     qr_url = request.build_absolute_uri()
#     host_url = request.scheme+'://'+request.META['HTTP_HOST'] 
#     context = {
#         'host_url': host_url,
#         'qr_url': qr_url,
#         'qaa': qaa
#     }
#     response = generate_document(request, report_type, tmpl_ctx)
    
#     return response

def report_generate(request, report_type, id):
    template_path = ''
    if report_type == 'score_letter':
        template_path = 'pdf/score_letter.html'
    elif report_type == 'qlassic_report':
        template_path = 'pdf/qlassic_report.html'
    elif report_type == 'qlassic_certificate':
        template_path = 'pdf/qlassic_certificate.html'
    else:
        raise Http404

    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    qr_url = request.build_absolute_uri()
    host_url = request.scheme+'://'+request.META['HTTP_HOST'] 
    context = {
        'host_url': host_url,
        'qr_url': qr_url,
        'qaa': qaa
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    response['Content-Disposition'] = 'inline; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

from .helpers.letter_templates import generate_training_document

from core.helpers import send_email_with_attachment
from trainings.models import RegistrationTraining
from api.soap.create_transaction import get_kodhasil, cancel_proforma

from api.jobs import job_update_contractor_info

@login_required(login_url="/login/")
def sandbox(request):
    # job_update_contractor_info()
    qaa = QlassicAssessmentApplication.objects.get(qaa_number="NS21 BP0001 C (P)")
    aa = get_qaa_result(qaa)
    print(aa)
    return JsonResponse(aa)

@login_required(login_url="/login/")
def generate_pdf(request):
    template_path = 'pdf/score_letter.html'
    qaa = QlassicAssessmentApplication.objects.all()[:0]
    context = {
        'qaa': qaa
    }
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)

    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

### Admin - Management Module ###
@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_defect_group(request):
    defect_groups = DefectGroup.objects.all()
    form_defect_group = DefectGroupCreateForm()
    if request.method == 'POST':
        if 'create' in request.POST:
            form_defect_group = DefectGroupCreateForm(request.POST)
            if form_defect_group.is_valid():
                form_defect_group.save()
                messages.info(request, 'Created successfully')
            else:
                messages.warning(request, 'Unable to create new defect group')

        return redirect('dashboard_defect_group')
    context = {"defect_groups": defect_groups, 'form_defect_group': form_defect_group}
    return render(request, "dashboard/management/defect_group.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_defect_group_id(request, id):
    defect_group = get_object_or_404(DefectGroup, id=id)
    form_defect_group = DefectGroupCreateForm(instance=defect_group)
    if request.method == 'POST':
        if 'delete' in request.POST:
            defect_group.delete()
            messages.info(request, 'Deleted successfully')
            return redirect('dashboard_defect_group')
        if 'update' in request.POST:
            form_defect_group = DefectGroupCreateForm(request.POST,instance=defect_group)
            if form_defect_group.is_valid():
                form_defect_group.save()
                messages.info(request, 'Updated successfully')
            else:
                messages.warning(request, 'Unable to update defect_group')

        return redirect('dashboard_defect_group_id', id)
    context = {"defect_group": defect_group,'form_defect_group':form_defect_group}
    return render(request, "dashboard/management/defect_group_id.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_sub_component(request):
    sub_components = SubComponent.objects.all()
    form_sub_component = SubComponentCreateForm()
    if request.method == 'POST':
        if 'create' in request.POST:
            form_sub_component = SubComponentCreateForm(request.POST)
            if form_sub_component.is_valid():
                form_sub_component.save()
                messages.info(request, 'Created successfully')
            else:
                messages.warning(request, 'Unable to create new sub_component')

        return redirect('dashboard_sub_component')
    context = {"sub_components": sub_components, 'form_sub_component': form_sub_component}
    return render(request, "dashboard/management/sub_component.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_sub_component_id(request, id):
    sub_component = get_object_or_404(SubComponent, id=id)
    form_sub_component = SubComponentCreateForm(instance=sub_component)
    if request.method == 'POST':
        if 'delete' in request.POST:
            sub_component.delete()
            messages.info(request, 'Deleted successfully')
            return redirect('dashboard_sub_component')
        if 'update' in request.POST:
            form_sub_component = SubComponentCreateForm(request.POST,instance=sub_component)
            if form_sub_component.is_valid():
                form_sub_component.save()
                messages.info(request, 'Updated successfully')
            else:
                messages.warning(request, 'Unable to update sub_component')

        return redirect('dashboard_sub_component_id', id)
    context = {"sub_component": sub_component,'form_sub_component':form_sub_component}
    return render(request, "dashboard/management/sub_component_id.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_component(request):
    components = Component.objects.all()
    form_component = ComponentCreateForm()
    if request.method == 'POST':
        if 'create' in request.POST:
            form_component = ComponentCreateForm(request.POST)
            if form_component.is_valid():
                form_component.save()
                messages.info(request, 'Created successfully')
            else:
                messages.warning(request, 'Unable to create new component')

        return redirect('dashboard_component')
    context = {"components": components, 'form_component': form_component}
    return render(request, "dashboard/management/component.html", context)

@login_required(login_url="/login/") 
@allowed_users(allowed_roles=['superadmin'])
def dashboard_component_id(request, id):
    component = get_object_or_404(Component, id=id)
    form_component = ComponentCreateForm(instance=component)
    if request.method == 'POST':
        if 'delete' in request.POST:
            component.delete()
            messages.info(request, 'Deleted successfully')
            return redirect('dashboard_component')
        if 'update' in request.POST:
            form_component = ComponentCreateForm(request.POST,instance=component)
            if form_component.is_valid():
                form_component.save()
                messages.info(request, 'Updated successfully')
            else:
                messages.warning(request, 'Unable to update component')

        return redirect('dashboard_component_id', id)
    context = {"component": component,'form_component':form_component}
    return render(request, "dashboard/management/component_id.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_element(request):
    elements = Element.objects.all()
    form_element = ElementCreateForm()
    if request.method == 'POST':
        if 'create' in request.POST:
            form_element = ElementCreateForm(request.POST)
            if form_element.is_valid():
                form_element.save()
                messages.info(request, 'Created successfully')
            else:
                messages.warning(request, 'Unable to create new element.')

        return redirect('dashboard_element')
    context = {"elements": elements, 'form_element': form_element}
    return render(request, "dashboard/management/element.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_element_id(request, id):
    element = get_object_or_404(Element, id=id)
    form_element = ElementCreateForm(instance=element)
    if request.method == 'POST':
        if 'delete' in request.POST:
            element.delete()
            messages.info(request, 'Deleted successfully')
            return redirect('dashboard_element')
        if 'update' in request.POST:
            form_element = ElementCreateForm(request.POST,instance=element)
            if form_element.is_valid():
                form_element.save()
                messages.info(request, 'Updated successfully')
            else:
                messages.warning(request, 'Unable to update element.')

        return redirect('dashboard_element_id', id)
    context = {"element": element,'form_element':form_element}
    return render(request, "dashboard/management/element_id.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_management_letter_id(request, id):
    context = {
    }
    return render(request, "dashboard/management/letter_id.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_management_letter(request):
    context = {
    }
    return render(request, "dashboard/management/letter.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_verified_contractor(request):
    vcs = VerifiedContractor.objects.all()
    form_vc = VerifiedContractorForm()
    if request.method == 'POST':
        if 'create' in request.POST:
            form_vc = VerifiedContractorForm(request.POST)
            contractor_registration_number = request.POST['contractor_registration_number']

            found, error_message = verify_contractor(contractor_registration_number)

            if found is True:
                if form_vc.is_valid():
                    vc = form_vc.save()
                    messages.info(request, 'Created successfully')
                else:
                    messages.warning(request, 'Unable to create new verified contractor:'+form_vc.errors.as_text())
            else:
                messages.warning(request, error_message)

        return redirect('dashboard_verified_contractor')
    context = {"vcs": vcs, 'form_vc': form_vc}
    return render(request, "dashboard/management/verified_contractor.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_verified_contractor_id(request, id):
    vc = get_object_or_404(VerifiedContractor, id=id)
    form_vc = VerifiedContractorForm(instance=vc)
    if request.method == 'POST':
        if 'delete' in request.POST:
            vc.delete()
            messages.info(request, 'Deleted successfully')
            return redirect('dashboard_verified_contractor')
        if 'update' in request.POST:
            form_vc = VerifiedContractorForm(request.POST,instance=vc)
            contractor_registration_number = request.POST['contractor_registration_number']
            found, error_message = verify_contractor(contractor_registration_number)
            if found is True:
                if form_vc.is_valid():
                    form_vc.save()
                    messages.info(request, 'Updated successfully')
                else:
                    messages.warning(request, 'Unable to update verified contractor:'+form_vc.errors.as_text())
            else:
                messages.warning(request, error_message)

        return redirect('dashboard_verified_contractor')
    context = {"vc": vc,'form_vc':form_vc}
    return render(request, "dashboard/management/verified_contractor_id.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_letter_template(request):
    letter_templates = LetterTemplate.objects.all().filter(training_type=None)
    form_letter_template = LetterTemplateCreateForm()
    
    # Check Template Existence
    for tt in TEMPLATE_TYPE:
        lt = LetterTemplate.objects.all().filter(template_type=tt[0],is_active=True)
        if len(lt) > 0:
            pass
        else:
            messages.warning(request, "Template '" + tt[1] + "' does not exist or inactive. Please upload the following template.")

    if request.method == 'POST':
        if 'create' in request.POST:
            form_letter_template = LetterTemplateCreateForm(request.POST,request.FILES)
            if form_letter_template.is_valid():
                form_letter_template.save()
                messages.info(request, 'Created successfully')
            else:
                messages.warning(request, 'Unable to create new letter template: '+form_letter_template.errors.as_text())
        if 'test_template' in request.POST:
            id = request.POST['id']
            template_type = request.POST['template_type']
            response = test_letter_template(id, template_type)
            return response

        return redirect('dashboard_letter_template')
    context = {"letter_templates": letter_templates, 'form_letter_template': form_letter_template}
    return render(request, "dashboard/management/letter_template.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_letter_template_id(request, id):
    letter_template = get_object_or_404(LetterTemplate, id=id)
    form_letter_template = LetterTemplateCreateForm(instance=letter_template)
    if request.method == 'POST':
        if 'delete' in request.POST:
            letter_template.delete()
            messages.info(request, 'Deleted successfully')
            return redirect('dashboard_letter_template')
        if 'update' in request.POST:
            form_letter_template = LetterTemplateCreateForm(request.POST,request.FILES,instance=letter_template)
            if form_letter_template.is_valid():
                form_letter_template.save()
                messages.info(request, 'Updated successfully')
            else:
                messages.warning(request, 'Unable to update letter_template')

        return redirect('dashboard_letter_template_id', id)
    context = {"letter_template": letter_template,'form_letter_template':form_letter_template}
    return render(request, "dashboard/management/letter_template_id.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_training_type(request):
    training_types = TrainingType.objects.all()
    form_training_type = TrainingTypeCreateForm()
    form_letter_template = LetterTemplateTrainingCreateForm()
    if request.method == 'POST':
        if 'create' in request.POST:
            form_training_type = TrainingTypeCreateForm(request.POST,request.FILES)
            form_letter_template = LetterTemplateTrainingCreateForm(request.POST,request.FILES)
            if form_training_type.is_valid():
                if form_letter_template.is_valid():
                    training_type = form_training_type.save()
                    letter_template = form_letter_template.save()
                    letter_template.training_type = training_type
                    letter_template.title = training_type.name
                    letter_template.type = training_type.name
                    letter_template.save()
                    messages.info(request, 'Created successfully')
                else:
                    messages.warning(request, 'Unable to create new training type: '+form_training_type.errors.as_text())
            else:
                messages.warning(request, 'Unable to create new training type: '+form_training_type.errors.as_text())

        return redirect('dashboard_training_type')
    context = {"training_types": training_types, 'form_training_type': form_training_type, 'form_letter_template': form_letter_template}
    return render(request, "dashboard/management/training_type.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_training_type_id(request, id):
    training_type = get_object_or_404(TrainingType, id=id)
    letter_template = get_object_or_404(LetterTemplate, training_type=training_type)
    form_training_type = TrainingTypeCreateForm(instance=training_type)
    form_letter_template = LetterTemplateTrainingCreateForm(instance=letter_template)
    if request.method == 'POST':
        if 'delete' in request.POST:
            letter_template.delete()
            training_type.delete()
            messages.info(request, 'Deleted successfully')
            return redirect('dashboard_training_type')
        if 'update' in request.POST:
            form_training_type = TrainingTypeCreateForm(request.POST,request.FILES,instance=training_type)
            form_letter_template = LetterTemplateTrainingCreateForm(request.POST,request.FILES,instance=letter_template)
            if form_training_type.is_valid():
                if form_letter_template.is_valid():
                    form_training_type.save()
                    form_letter_template.save()
                    messages.info(request, 'Updated successfully')
                else:
                    messages.warning(request, 'Unable to update training type')
            else:
                messages.warning(request, 'Unable to update training type')

        return redirect('dashboard_training_type_id', id)
    context = {"training_type": training_type,'form_training_type':form_training_type, 'form_letter_template':form_letter_template}
    return render(request, "dashboard/management/training_type_id.html", context)

# @login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template( load_template )
        return HttpResponse(html_template.render(context, request))
        
    except template.TemplateDoesNotExist:

        html_template = loader.get_template( 'page-404.html' )
        return HttpResponse(html_template.render(context, request))

    except:
    
        html_template = loader.get_template( 'page-500.html' )
        return HttpResponse(html_template.render(context, request))

from django.db.models import Count, Sum

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_manage_component_v2(request):
    components = Component.objects.all()
    elements = Element.objects.all().filter(category_weightage=True)
    total_weightage_a = components.aggregate(Sum('weightage_a'))
    total_weightage_b = components.aggregate(Sum('weightage_b'))
    total_weightage_c = components.aggregate(Sum('weightage_c'))
    total_weightage_d = components.aggregate(Sum('weightage_d'))
    total_weightage_element_a = elements.aggregate(Sum('weightage_a'))
    total_weightage_element_b = elements.aggregate(Sum('weightage_b'))
    total_weightage_element_c = elements.aggregate(Sum('weightage_c'))
    total_weightage_element_d = elements.aggregate(Sum('weightage_d'))
    tw_a = 0
    tw_b = 0
    tw_c = 0
    tw_d = 0
    tw_element_a = 0
    tw_element_b = 0
    tw_element_c = 0
    tw_element_d = 0
    if total_weightage_a['weightage_a__sum'] == None:
        tw_a = 0
    else:
        tw_a = total_weightage_a['weightage_a__sum']
    if total_weightage_b['weightage_b__sum'] == None:
        tw_b = 0
    else:
        tw_b = total_weightage_b['weightage_b__sum']
    if total_weightage_c['weightage_c__sum'] == None:
        tw_c = 0
    else:
        tw_c = total_weightage_c['weightage_c__sum']
    if total_weightage_d['weightage_d__sum'] == None:
        tw_d = 0
    else:
        tw_d = total_weightage_d['weightage_d__sum']
    if total_weightage_element_a['weightage_a__sum'] == None:
        tw_element_a = 0
    else:
        tw_element_a = total_weightage_element_a['weightage_a__sum']
    if total_weightage_element_b['weightage_b__sum'] == None:
        tw_element_b = 0
    else:
        tw_element_b = total_weightage_element_b['weightage_b__sum']
    if total_weightage_element_c['weightage_c__sum'] == None:
        tw_element_c = 0
    else:
        tw_element_c = total_weightage_element_c['weightage_c__sum']
    if total_weightage_element_d['weightage_d__sum'] == None:
        tw_element_d = 0
    else:
        tw_element_d = total_weightage_element_d['weightage_d__sum']
    form = ComponentCreateForm()
    context = {
        'mode':'component',
        'title': 'Components',
        'form': form,
        'total_weightage_a':tw_a + tw_element_a,
        'total_weightage_b':tw_b + tw_element_b,
        'total_weightage_c':tw_c + tw_element_c,
        'total_weightage_d':tw_d + tw_element_d,
        'components':components,
        'elements':elements,
    }

    if request.method == 'POST':
        form = ComponentCreateForm(request.POST)
        if form.is_valid():
            form_data = form.save()
            form_data.created_by = request.user.name
            form_data.modified_by = request.user.name
            form_data.save()
            messages.info(request,'Successfully created new component')
        else:
            messages.warning(request,'Error creating new component')
        return redirect('dashboard_manage_component_v2')
    return render(request, "dashboard/management/manage_component_v2.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_manage_sub_component_v2(request, mode, id):
    parent = None
    total_weightage = 0
    children = None
    title = ''
    form = None
    check_loop = None
    if mode == 'sub_component':
        parent = get_object_or_404(Component,id=id)
        children = SubComponent.objects.all().filter(component=parent)
        
        for child in children:
            total_weightage += child.get_total_weightage()
            
        form = SubComponentCreateForm()
        title = 'Sub Components'
    if mode == 'element':
        parent = get_object_or_404(SubComponent,id=id)
        children = Element.objects.all().filter(sub_component=parent)
        form = ElementCreateForm()
        title = 'Elements'
    if mode == 'defect_group':
        parent = get_object_or_404(Element,id=id)
        children = DefectGroup.objects.all().filter(element=parent)
        form = DefectGroupCreateForm()
        title = 'Defect Groups'
        check_loop = range(parent.no_of_check)
    context = {
        'mode':mode,
        'parent':parent,
        'children':children,
        # 'special_elements':special_elements,
        'title': title,
        'form': form,
        'total_weightage':total_weightage,
        'check_loop': check_loop
    }

    if request.method == 'POST':
        if mode == 'sub_component':
            form = SubComponentCreateForm(request.POST)
        if mode == 'element':
            form = ElementCreateForm(request.POST)
        if mode == 'defect_group':
            form = DefectGroupCreateForm(request.POST)
        if form.is_valid():
            form_data = form.save()
            form_data.created_by = request.user.name
            form_data.modified_by = request.user.name
            if mode == 'sub_component':
                form_data.component = parent
                messages.info(request,'Successfully created new sub component')
            if mode == 'element':
                form_data.sub_component = parent
                messages.info(request,'Successfully created new element')
            if mode == 'defect_group':
                form_data.element = parent
                messages.info(request,'Successfully created new defect group')
            form_data.save()
        else:
            messages.warning(request,'Problem creating a new entry')
        return redirect('dashboard_manage_sub_component_v2', mode, parent.id)
    return render(request, "dashboard/management/manage_component_v2.html", context)

from assessments.forms import (
    ComponentEditForm,
    SubComponentEditForm,
    ElementEditForm,
    DefectGroupEditForm,
    # ElementWithWeightageEditForm,
)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_manage_edit_component_v2(request, mode, id):
    children = None
    parent = None
    form = None
    title=''
    if mode == 'component':
        children = get_object_or_404(Component,id=id)
        form = ComponentEditForm(instance=children)
        title = 'Component'
    if mode == 'sub_component':
        children = get_object_or_404(SubComponent,id=id)
        parent = children.component
        form = SubComponentEditForm(instance=children)
        title = 'Sub Component'
    if mode == 'element':
        children = get_object_or_404(Element,id=id)
        parent = children.sub_component
        # if children.sub_component_weightage == True:
        #     form = ElementWithWeightageEditForm(instance=children)
        # else:
        form = ElementEditForm(instance=children)
        title = 'Element'
    if mode == 'defect_group':
        children = get_object_or_404(DefectGroup,id=id)
        parent = children.element
        form = DefectGroupEditForm(instance=children)
        title = 'Defect Group'
    context = {
        'mode':mode,
        'form':form,
        'children':children,
        'title':title,
        'parent':parent,
    }

    if request.method == 'POST':
        if 'update' in request.POST:
            if mode == 'component':
                form = ComponentEditForm(request.POST, instance=children)
            elif mode == 'sub_component':
                form = SubComponentEditForm(request.POST, instance=children)
            elif mode == 'element':
                # if children.sub_component_weightage == True:
                #     form = ElementWithWeightageEditForm(request.POST, instance=children)
                # else:
                form = ElementEditForm(request.POST, instance=children)
            elif mode == 'defect_group':
                form = DefectGroupEditForm(request.POST, instance=children)
            else:
                pass
            if form.is_valid():
                form_data = form.save()
                form_data.modified_by = request.user.name
                form_data.save()
                messages.info(request,'Updated successfully')
            else:
                messages.warning(request,'Problem updating the data')
            return redirect('dashboard_manage_edit_component_v2', mode, children.id)
        if 'delete' in request.POST:
            parent_id = ''
            if mode == 'sub_component':
                parent_id = parent.id
            if mode == 'element':
                parent_id = parent.id
            if mode == 'defect_group':
                parent_id = parent.id
            children.delete()
            messages.info(request,'Successfully deleted the data')
            
            if mode == 'component':
                return redirect('dashboard_manage_component_v2')
            return redirect('dashboard_manage_sub_component_v2', mode, parent_id)
    return render(request, "dashboard/management/manage_component_edit_v2.html", context)


# assessment detail page
# ISRAA CODES START HERE

@login_required(login_url="/login/")
def assessment_report_detail(request, id):
    init = int(time())
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    component_type = "Architectural Works"
    subcomponent_type = "Internal Finishes"
    
    try:
        component = Component.objects.all().filter(name=component_type)
        sub_component = SubComponent.objects.all().get(name=subcomponent_type)

    except Exception as e:
        component_type = component_type.upper()
        subcomponent_type = subcomponent_type.upper()

        component = Component.objects.all().filter(name=component_type)
        sub_component = SubComponent.objects.all().get(name=subcomponent_type)


    elements = Element.objects.all().filter(sub_component=sub_component)
    sample_results = SampleResult.objects.all().filter(qaa=qaa)

    context = {}
    ret = []
    for element in elements:
        temp = {} 
        temp2 = []
        
        element_results = ElementResult.objects.all().filter(
            Q(qaa=qaa,element_code=element.id)|
            Q(qaa=qaa,element_code=element.code_id)
        )

        sr = set([i.sample_result for i in element_results])
        column_headers = ["Block", "Unit", "Type", "Selection Value"]
        #dg = DefectGroup.objects.all().filter(element=element)

        dg = set([i.dg_name for i in element_results])
        for i in dg:
            column_headers.append(i)

        column_results = []
           
        for s in sr:
            #er = ElementResult.objects.all().filter(sample_result = s)
            er = ElementResult.objects.all().filter(
                Q(qaa=qaa,element_code=element.id, sample_result = s)|
                Q(qaa=qaa,element_code=element.code_id, sample_result = s)
            )

            sub = []
            sub.append(s.block)
            sub.append(s.unit)
            sub.append(s.test_type)
            sub.append(s.selection_value)

            for d in dg:
                for e in er:
                    if e.dg_name == d:
                        sub.append(e.result)

            try:
                a = "<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_1.url)+">1</a>&nbsp<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_2.url)+">2</a>&nbsp<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_3.url)+">3</a>&nbsp<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_4.url)+">4</a>"
                sub.append(a)
            except Exception as e:
                pass

            column_results.append(sub)

        column_headers.append("Photos")
        temp = {
            "element_name": element.name,
            "column_headers": column_headers,
            "column_results": column_results, 
        }

        ret.append(temp)

    ret.reverse()
    context['data'] = ret

    print(int(time()) - init)
    
    if request.method == 'POST':
        pass
    return render(request, "dashboard/reporting/assessment_detail.html", context)


@login_required(login_url="/login/")
def assessment_report_detail_ef(request, id):
    init = int(time())
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)

    component_type = "Architectural Works"
    subcomponent_type = "External Finishes"
    
    try:
        component = Component.objects.all().filter(name=component_type)
        sub_component = SubComponent.objects.all().get(name=subcomponent_type)

    except Exception as e:
        component_type = component_type.upper()
        subcomponent_type = subcomponent_type.upper()

        component = Component.objects.all().filter(name=component_type)
        sub_component = SubComponent.objects.all().get(name=subcomponent_type)


    elements = Element.objects.all().filter(sub_component=sub_component)
    sample_results = SampleResult.objects.all().filter(qaa=qaa)

    context = {}
    ret = []
    for element in elements:
        temp = {} 
        temp2 = []
        
        element_results = ElementResult.objects.all().filter(
            Q(qaa=qaa,element_code=element.id)|
            Q(qaa=qaa,element_code=element.code_id)
        )


        sr = set([i.sample_result for i in element_results])
        column_headers = []

        dg = set([i.dg_name for i in element_results])
        for i in dg:
            column_headers.append(i)

        column_results = []
           
        for s in sr:
            er = ElementResult.objects.all().filter(
                Q(qaa=qaa,element_code=element.id, sample_result = s)|
                Q(qaa=qaa,element_code=element.code_id, sample_result = s)
            )

            sub = []

            for d in dg:
                for e in er:
                    if e.dg_name == d:
                        sub.append(e.result)


            try:
                a = "<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_1.url)+">1</a>&nbsp<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_2.url)+">2</a>&nbsp<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_3.url)+">3</a>&nbsp<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_4.url)+">4</a>"
                sub.append(a)
            except Exception as e:
                pass
            
        
            column_results.append(sub)

        column_headers.append("Photos")

        temp = {
            "element_name": element.name,
            "column_headers": column_headers,
            "column_results": column_results, 
        }

        ret.reverse()
        ret.append(temp)
    context['data'] = ret

    print(int(time()) - init)
    
    if request.method == 'POST':
        pass
    return render(request, "dashboard/reporting/assessment_detail.html", context)


@login_required(login_url="/login/")
def assessment_report_detail_ew(request, id):
    init = int(time())
    qaa = get_object_or_404(QlassicAssessmentApplication, id=id)
    component = Component.objects.all().filter(name="Architectural Works")

    subcomponent_type = "Infrastructure"
    try:
        sub_component = SubComponent.objects.all().get(name=subcomponent_type)
    except Exception as e:
        subcomponent_type = subcomponent_type.upper()
        sub_component = SubComponent.objects.all().get(name=subcomponent_type)

    elements = Element.objects.all().filter(sub_component=sub_component)

    sample_results = SampleResult.objects.all().filter(qaa=qaa)

    context = {}
    ret = []
    for element in elements:
        temp = {} 
        temp2 = []
        
        element_results = ElementResult.objects.all().filter(
            Q(qaa=qaa,element_code=element.id)|
            Q(qaa=qaa,element_code=element.code_id)
        )


        sr = set([i.sample_result for i in element_results])
        column_headers = []
        #dg = DefectGroup.objects.all().filter(element=element)

        dg = set([i.dg_name for i in element_results])
        for i in dg:
            column_headers.append(i)

        column_results = []
           
        for s in sr:
            #er = ElementResult.objects.all().filter(sample_result = s)
            er = ElementResult.objects.all().filter(
                Q(qaa=qaa,element_code=element.id, sample_result = s)|
                Q(qaa=qaa,element_code=element.code_id, sample_result = s)
            )

            sub = []

            for d in dg:
                for e in er:
                    if e.dg_name == d:
                        sub.append(e.result)

            try:
                a = "<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_1.url)+">1</a>&nbsp<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_2.url)+">2</a>&nbsp<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_3.url)+">3</a>&nbsp<a class='btn btn-sm btn-default mb-2' href="+str(s.photo_4.url)+">4</a>"
                sub.append(a)
            except Exception as e:
                pass

        
            column_results.append(sub)

        column_headers.append("Photos")
        temp = {
            "element_name": element.name,
            "column_headers": column_headers,
            "column_results": column_results, 
        }

        ret.append(temp)
        ret.reverse()
    context['data'] = ret

    print(int(time()) - init)
    
    if request.method == 'POST':
        pass
    return render(request, "dashboard/reporting/assessment_detail.html", context)

@login_required(login_url="/login/")
def assessment_attendance_detail(request, id):
    qaa = QlassicAssessmentApplication.objects.get(id=id)
    sa = SiteAttendance.objects.all().filter(qaa=qaa)
    context = {"sa":sa}
       
    return render(request, "dashboard/reporting/attendance_detail.html", context)



@login_required(login_url="/login/")
def assessment_report_detail_result(request, id):
    sample_result = SampleResult.objects.get(id=id) 
    element_results = ElementResult.objects.all().filter(sample_result = sample_result)
    print(len(element_results))
    dg_names_list = set([i.dg_name for i in element_results])

    temp = {}
    for i in dg_names_list:
        temp[i] = []

    for dgn in dg_names_list:
        for er in element_results:
            if er.dg_name == dgn:
                temp[dgn].append(er.total_check)

    dg_values = []
    for i in dg_names_list:
        s = sum(temp[i])
        dg_values.append(s)

    
    context = {
        "dg_names": dg_names_list,
        "dg_values": dg_values,
    }
    ret = []

    if request.method == 'POST':
        pass
    return render(request, "dashboard/reporting/assessment_detail_result.html", context)


### Functions ###

def assessment_report_generate(request, report_type, qaa):
    template_ctx = ''
    reporting, created = QlassicReporting.objects.get_or_create(qaa=qaa,report_type=report_type)
    #qr_path = absoluteuri.build_absolute_uri('/cert_assessment/'+report_type+'/'+str(qaa.id)+'/')
    #qr_path = f"https://qlassic.cidb.gov.my/reportpdf/{qaa.id}"

    #generate_and_save_qr(qr_path, reporting.qr_file)

    # print qr directory

    qlassic_score = get_qlassic_score(qaa)
    rounded_qlassic_score = str(int(round(qlassic_score)))
    
    if qaa.no_of_days > 1:
        period = qaa.no_of_days - 1
        end_date = qaa.assessment_date + timedelta(hours=period*24)

        assessment_date = f"{translate_malay_date(standard_date(qaa.assessment_date))} - {standard_date(end_date)}"
    if qaa.no_of_days == 1:
        assessment_date = translate_malay_date(standard_date(qaa.assessment_date))

    if report_type == 'qlassic_score_letter':
        
        qr_path = f"https://qlassic.cidb.gov.my/reportpdf_score/{qaa.id}"

        #qr_path = f"https://qlassicstg.cidb.gov.my/reportpdf_score/{qaa.id}"
        print("assessment_date", assessment_date)
        generate_and_save_qr(qr_path, reporting.qr_file)


        template_ctx = {
            'title': qaa.pi.project_title,
            'id': reporting.code_id,
            'qaa_number': qaa.qaa_number,
            'assessment_date': assessment_date,
            'now': translate_malay_date(standard_date(datetime.now())),
            'developer': qaa.pi.developer,
            'developer_ssm_number': qaa.pi.developer_ssm_number,
            'contractor': qaa.pi.contractor_name,
            'cidb_number': qaa.pi.contractor_cidb_registration_no,
            'grade': qaa.pi.contractor_registration_grade,
            'ccd_score': str(int(round(qaa.ccd_point, 2))),
            'qlassic_score': rounded_qlassic_score,
        }
        response_cert = generate_document_file(request, report_type, template_ctx, reporting.qr_file)
        reporting.report_file.save('pdf', response_cert)
    elif report_type == 'qlassic_report':
        qaa_result = get_qaa_result(qaa)
        assessors = AssignedAssessor.objects.all().filter(ad__qaa=qaa)
        assessors = filterRepeatedName(assessors)


        casc_score = rounded_qlassic_score
        if qaa.casc_qlassic_score != None:
            casc_score = str(round(qaa.casc_qlassic_score, 2))
        template_ctx = {
            'title': qaa.pi.project_title,
            'id': reporting.code_id,
            'qaa_number': qaa.qaa_number,
            'assessment_date': assessment_date,
            'now': translate_malay_date(standard_date(datetime.now())),
            'assessors': rs,
            'gfa': qaa.pi.gfa,
            'project_value': qaa.pi.contract_value,
            'developer': qaa.pi.developer,
            'developer_ssm_number': qaa.pi.developer_ssm_number,
            'contractor': qaa.pi.contractor_name,
            'site_representative': qaa.pi.site_representative,
            'project_manager': qaa.pi.project_manager,
            'cidb_number': qaa.pi.contractor_cidb_registration_no,
            'grade': qaa.pi.contractor_registration_grade,
            'architect_firm': qaa.pi.architect_firm,
            'structural_civil_engineer_firm': qaa.pi.structural_civil_engineer_firm,
            'mechanical_electrical_firm': qaa.pi.mechanical_electrical_firm,
            'ccd_score': str(int(round(qaa.ccd_point, 2))),
            'qlassic_score': '{:.2f}'.format(qaa.qlassic_score),
            'casc_qlassic_score': casc_score,
            'qaa_result': qaa_result,
            'weather': qaa_result['weather'],
            'sample': qaa_result['sample'],
            'components': qaa_result['components'],
            'scope': qaa_result['scope'],
        }
        response_cert = generate_document_file(request, report_type, template_ctx, None)
        reporting.report_file.save('pdf', response_cert)


    elif report_type == 'qlassic_certificate':
        qr_path = f"https://qlassic.cidb.gov.my/reportpdf_certificate/{qaa.id}"
        generate_and_save_qr(qr_path, reporting.qr_file)

        scope = Scope.objects.all().filter(qaa=qaa)
        scope = [i.scope for i in scope]
        template_ctx = {
            'title': qaa.pi.project_title,
            'id': reporting.code_id,
            'qaa_number': qaa.qaa_number,
            'assessment_date': assessment_date,
            'now': translate_malay_date(standard_date(datetime.now())),
            'developer': qaa.pi.developer,
            'developer_ssm_number': qaa.pi.developer_ssm_number,
            'contractor': qaa.pi.contractor_name,
            'cidb_number': qaa.pi.contractor_cidb_registration_no,
            'grade': qaa.pi.contractor_registration_grade,
            'ccd_score': str(int(round(qaa.ccd_point, 2))),
            'qlassic_score': rounded_qlassic_score,
            'scope': scope
        }
        response_cert = generate_document_file(request, report_type, template_ctx, reporting.qr_file)
        reporting.report_file.save('pdf', response_cert)

    else:
        return None

    
    return reporting

def getPdfCertificate(request, id):
    reporting = QlassicReporting.objects.get(qaa=id, report_type="qlassic_certificate")
    return redirect(reporting.report_file.url)

def getPdfScore(request, id):
    reporting = QlassicReporting.objects.get(qaa=id, report_type="qlassic_score_letter")
    return redirect(reporting.report_file.url)

def filterRepeatedName(assessors):
    ret = []
    names = list(set([i.name for i in assessors]))
    for name in names:
        temp = {}
        temp["name"] = name
        ret.append(temp)
        
    return ret



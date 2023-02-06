from django.contrib import messages
from .models import RegistrationTraining, RoleApplication, RoleApplication
from assessments.models import SupportingDocuments
from .forms import RoleApplicationSupportingDocumentsUploadForm
from django.db.models import Q

def check_available_seat(request, training):
    registered = RegistrationTraining.objects.all().filter(training=training)
    current_seat = registered.filter(
        Q(status="accepted")|
        Q(status="need_payment")
    ).count()
    available_seat = training.size - current_seat
    available = True
    if available_seat < 1:
        messages.warning(request, 'There is no available seat')
        available = False
    return available_seat, available

def get_trainer_application(request, user):
    application = None
    applicable = True
    ats = RoleApplication.objects.all().filter(user=user,application_type='trainer').order_by('-created_date')
    if len(ats) > 0:
        at = ats[0]
        if at.application_status == '':
            applicable = True
            application = at
        elif at.application_status == 'pending':
            applicable = False
            messages.warning(request, 'Please wait for approval of previous application before reapplying.')
        elif at.application_status == 'reject':
            application = RoleApplication.objects.create(user=user,application_type='trainer')
            applicable = True
        elif at.application_status == 'approved':
            applicable = False
            messages.warning(request, 'You are already a trainer.')
        else:
            applicable = False
    else:
        application = RoleApplication.objects.create(user=user,application_type='trainer')
        applicable = True
    return application, applicable

def get_assessor_application(request, user):
    application = None
    applicable = True
    ats = RoleApplication.objects.all().filter(user=user,application_type='qca').order_by('-created_date')
    if len(ats) > 0:
        at = ats[0]
        if at.application_status == '':
            applicable = True
            application = at
        elif at.application_status == 'pending':
            applicable = False
            messages.warning(request, 'Please wait for approval of previous application before reapplying.')
        elif at.application_status == 'reject':
            application = RoleApplication.objects.create(user=user,application_type='qca')
            applicable = True
        elif at.application_status == 'approved':
            applicable = False
            messages.warning(request, 'You are already a QLASSIC CIDB Assessor.')
        else:
            applicable = False
    else:
        application = RoleApplication.objects.create(user=user,application_type='qca')
        applicable = True
    return application, applicable


def get_trainer_application_status(user):
    application = None
    applicable = True

    if not user.is_assessor and not user.is_trainer and user.role != 'superadmin':
        applicable = False
        return (application, applicable)

    ats = RoleApplication.objects.all().filter(user=user,application_type='trainer').order_by('-created_date')
    if len(ats) > 0:
        application = ats[0]
        if application.application_status == '':
            applicable = True
        elif application.application_status == 'pending':
            applicable = False
        elif application.application_status == 'reject':
            applicable = True
        elif application.application_status == 'approved':
            applicable = False
        else:
            applicable = False
    else:
        application = None
        applicable = True
    return application, applicable

def get_assessor_application_status(user):
    application = None
    applicable = True

    if not user.is_assessor and not user.is_trainer and user.role != 'superadmin':
        applicable = False
        return (application, applicable)
        
    ats = RoleApplication.objects.all().filter(user=user,application_type='qca').order_by('-created_date')
    if len(ats) > 0:
        application = ats[0]
        if application.application_status == '':
            applicable = True
        elif application.application_status == 'pending':
            applicable = False
        elif application.application_status == 'reject':
            applicable = True
        elif application.application_status == 'approved':
            applicable = False
        else:
            applicable = False
    else:
        application = None
        applicable = True
    return application, applicable

def get_role_application_supporting_documents(application):
    context = { 'sds': []}
    sds = SupportingDocuments.objects.all().filter(ra=application)
    sd_1, created = sds.get_or_create(ra=application, file_name='sd_ra_1')
    sd_2, created = sds.get_or_create(ra=application, file_name='sd_ra_2')
    sd_3, created = sds.get_or_create(ra=application, file_name='sd_ra_3')
    sd_4, created = sds.get_or_create(ra=application, file_name='sd_ra_4')
    sd_5, created = sds.get_or_create(ra=application, file_name='sd_ra_5')
    sd_6, created = sds.get_or_create(ra=application, file_name='sd_ra_6')

    context['sds'].append( {
        'title': 'A copy of the academic certificate related to the construction ( accredited by IPTA/IPTS)',
        'required': False,
        'sd': sd_1,
        }
    )
    context['sds'].append( {
        'title': 'Professional Qualification (Ir./Ar./Reg. Qs./ IOW) *If available',
        'required': False,
        'sd': sd_2,
        }
    )
    context['sds'].append( {
        'title': 'A copy of Identity Card',
        'required': False,
        'sd': sd_3,
        }
    )
    context['sds'].append( {
        'title': 'Resume (Related to Construction)',
        'required': False,
        'sd': sd_4,
        }
    )
    context['sds'].append( {
        'title': 'SSM Registration (self-employed)',
        'required': False,
        'sd': sd_5,
        }
    )
    context['sds'].append( {
        'title': 'Employer Confirmation Form',
        'required': False,
        'sd': sd_6,
        }
    )
    return context

def save_role_application_supporting_documents(request, application):
    sds = SupportingDocuments.objects.all().filter(ra=application)
    form = RoleApplicationSupportingDocumentsUploadForm()
    sd_1, created = sds.get_or_create(ra=application, file_name='sd_ra_1')
    sd_2, created = sds.get_or_create(ra=application, file_name='sd_ra_2')
    sd_3, created = sds.get_or_create(ra=application, file_name='sd_ra_3')
    sd_4, created = sds.get_or_create(ra=application, file_name='sd_ra_4')
    sd_5, created = sds.get_or_create(ra=application, file_name='sd_ra_5')
    sd_6, created = sds.get_or_create(ra=application, file_name='sd_ra_6')
    
    form = RoleApplicationSupportingDocumentsUploadForm(request.POST, request.FILES)
    success = False

    if form.is_valid():
        data_sd_1 = form.cleaned_data.get('sd_ra_1')
        data_sd_2 = form.cleaned_data.get('sd_ra_2')
        data_sd_3 = form.cleaned_data.get('sd_ra_3')
        data_sd_4 = form.cleaned_data.get('sd_ra_4')
        data_sd_5 = form.cleaned_data.get('sd_ra_5')
        data_sd_6 = form.cleaned_data.get('sd_ra_6')
        # print(type(data_sd_1))
        # print(type(data_sd_2))
        # print(type(data_sd_3))
        # print(type(data_sd_4))
        # print(type(data_sd_5))
        # print(type(data_sd_6))
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
        if 'save' in request.POST:
            messages.info(request,'Saved the documents.')
        if 'submit' in request.POST:
            messages.info(request,'Successfully submit the application.')
        success = True
    else:
        messages.warning(request,'Problem with submitting the application:'+form.errors.as_text())
        success = False

    return success

# def generate_role_application_number(application):
#     number = ''
#     if application.application_number == None:
#         applications = RoleApplication.objects.all().exclude(application_number=None).order_by('-created_date')
#         if len(applications) > 0:
#             latest = applications[0]
#             str_current_count = latest.application_number.replace('QRA','')
#             current_count = int(str_current_count)
#             current_count += 1
#             application.application_number = 'QRA' + str(current_count).zfill(6)
#             application.save()
#         else:
#             application.application_number = 'QRA' + str(1).zfill(6)
#             application.save()
#     return number

def get_pass_fail_translation(pass_status):
    if pass_status == True:
        return 'LULUS'
    else:
        return 'GAGAL'
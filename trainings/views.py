from datetime import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
import absoluteuri
from django.http import JsonResponse

# Decorators
from django.contrib.auth.decorators import login_required
from authentication.decorators import allowed_users

# Models
from .models import (
    RoleApplication,
    Coach,
    Training,
    RegistrationTraining,
    JoinedTraining,
    ORGANIZATION_TYPE_CHOICES,
    Feedback, TrainingType,
)

from users.models import (
    CustomUser, Trainer,
    Assessor,
    AcademicQualification, 
    WorkExperience,
)

from billings.models import Payment

# Forms
from .forms import (
    AttendanceSheetUploadForm,
    CoachCreateForm,
    TrainingCreateForm,
    RegistrationTrainingCreateForm,
    RegistrationTrainingReviewForm,
    FeedbackCreateForm,
    RoleApplicationInterviewForm,
    EditRoleApplicationForm,
)

# Helpers
from .helpers import (
    check_available_seat,
    get_trainer_application_status,
    get_assessor_application_status,
    get_trainer_application,
    get_assessor_application,
    get_role_application_supporting_documents,
    save_role_application_supporting_documents,
    # generate_role_application_number,
)
from billings.helpers import payment_response_process, get_payment_history_url

import absoluteuri

from core.helpers import translate_malay_date, standard_date, send_email_default, send_email_with_attachment, generate_and_save_qr, get_domain
from app.helpers.letter_templates import generate_document, generate_document_file, generate_training_document_file
from api.soap.create_transaction import create_transaction, cancel_proforma, create_training_transaction, get_receipt_url, payment_gateway_url

# Create your views here.
@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer', 'assessor', 'trainee', 'applicant'])
def dashboard_training_application_dashboard(request):
    if not request.user.is_assessor and not request.user.is_trainer and request.user.role != 'superadmin':
        messages.warning(request, 'You must be either QLASSIC Industry Assessor (QIA), QLASSIC CIDB Assessor (QCA) or Trainer in order to apply the role(s) below.')
    # application, applicable = get_trainer_application(request, request.user, 'trainer')
    application_trainer, applicable_trainer = get_trainer_application_status(request.user)
    application_assessor, applicable_assessor = get_assessor_application_status(request.user)
    assessor = Assessor.objects.all().filter(user=request.user).first()
    trainer = Trainer.objects.all().filter(user=request.user).first()
    context = {
        'assessor':assessor,
        'trainer':trainer,
        'application_trainer':application_trainer,
        'applicable_trainer':applicable_trainer,
        'application_assessor':application_assessor,
        'applicable_assessor':applicable_assessor,
    }
    return render(request, "dashboard/training/role_application_dashboard.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer'])
def dashboard_training_role_application_list(request):
    applications = RoleApplication.objects.all().exclude(application_status='').order_by('-modified_date')
    context = {
        'applications':applications,
    }
    return render(request, "dashboard/training/role_application_list.html", context)

@login_required
def edit_role_application(request, id):
        obj= get_object_or_404(RoleApplication, id=id)
        
        form = EditRoleApplicationForm(request.POST or None, instance= obj)
        context= {'form': form}

        if form.is_valid():
                obj= form.save(commit= False)

                obj.save()

                messages.success(request, "You successfully updated the data")
                return redirect('dashboard_training_role_application_list')
        else:
                context= {'form': form,
                           'error': 'The form was not updated successfully. Please enter in a title and content'}
        return render(request,"dashboard/training/edit_role_application_list.html", context)

# @allowed_users(allowed_roles=['superadmin', 'trainer'])
# @login_required(login_url="/login/")
# def dashboard_training_application_new(request):
#     context = {
#         'mode': 'step_1',
#     }
#     # if request.method == 'POST':
#     #     application_type = 
#     #     application, applicable = get_trainer_application(request, request.user, 'trainer')
#     return render(request, "dashboard/training/application_form.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer','assessor'])
def dashboard_training_application_new(request, application_type, step):
    context = {
        'application_type': application_type,
        'mode': step,
    }

    applicable = False
    application = None
    if application_type == 'qca':
        application, applicable = get_assessor_application(request, request.user)
        context['application'] = application
    if application_type == 'trainer':
        application, applicable = get_trainer_application(request, request.user)
        context['application'] = application
    if applicable:
        pass
    else:
        messages.warning(request, 'Unable to apply the role.')
        return redirect('dashboard_training_application_dashboard')
    
    if step == 'step-2':
        academic_qualifications = AcademicQualification.objects.all().filter(user=request.user)
        context['academic_qualifications'] = academic_qualifications
    
    if step == 'step-3':
        work_experiences = WorkExperience.objects.all().filter(user=request.user)
        context['work_experiences'] = work_experiences
    
    if step == 'step-4':
        registration_trainings = RegistrationTraining.objects.all().filter(user=request.user, status='accepted', attendance_full=True)
        joined_trainings = JoinedTraining.objects.all().filter(user=request.user)
        context['registration_trainings'] = registration_trainings
        context['joined_trainings'] = joined_trainings
        if request.method == 'POST':
            if 'add' in request.POST:
                jt_year = request.POST['year']
                jt_course = request.POST['course']
                jt_place = request.POST['place']
                jt = JoinedTraining.objects.create(user=request.user, year=jt_year, course=jt_course, place=jt_place)
                messages.info(request, 'Added the joined training info.')
            if 'delete' in request.POST:
                jt_id = request.POST['id']
                jt = JoinedTraining.objects.get(id=jt_id)
                jt.delete()
                messages.info(request, 'Deleted the joined training.')
            return redirect('dashboard_training_application_new', application_type, step)

    if step == 'step-5':
        work_experiences = WorkExperience.objects.all().filter(user=request.user)
        context['supporting_documents'] = get_role_application_supporting_documents(application)
        if request.method == 'POST':
            save_role_application_supporting_documents(request, application)
            if 'save' in request.POST:
                return redirect('dashboard_training_application_new', application_type, step)

            if 'submit' in request.POST:
                application.application_status = 'pending'
                # generate_role_application_number(application)
                application.save()

                 # Email
                to = []
                reviewers = CustomUser.objects.all().filter(
                    Q(role='superadmin')|
                    Q(role='cidb_reviewer')
                )
                for reviewer in reviewers:
                    to.append(reviewer.email)
                subject = "Role Application Submission - " + application.application_number
                ctx_email = {
                    'application':application,
                }
                messages.info(request, 'Successfully send the role application.')
                send_email_default(subject, to, ctx_email, 'email/role-application-submission.html')

                return redirect('dashboard_training_application_dashboard')

    return render(request, "dashboard/training/role_application_form.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer'])
def dashboard_training_role_application_review(request, id, step):
    application = get_object_or_404(RoleApplication, id=id)
    interview_form = RoleApplicationInterviewForm()
    context = {
        'review': True,
        'id': id,
        'application': application,
        'mode': step,
        'interview_form':interview_form,
    }

    if step == 'step-2':
        academic_qualifications = AcademicQualification.objects.all().filter(user=request.user)
        context['academic_qualifications'] = academic_qualifications
    
    if step == 'step-3':
        work_experiences = WorkExperience.objects.all().filter(user=request.user)
        context['work_experiences'] = work_experiences
    
    if step == 'step-4':
        registration_trainings = RegistrationTraining.objects.all().filter(user=request.user, status='accepted', attendance_full=True)
        joined_trainings = JoinedTraining.objects.all().filter(user=request.user)
        context['registration_trainings'] = registration_trainings
        context['joined_trainings'] = joined_trainings

    if step == 'step-5':
        work_experiences = WorkExperience.objects.all().filter(user=request.user)
        context['supporting_documents'] = get_role_application_supporting_documents(application)

    if request.method == "POST":
        if 'interview' in request.POST:
            # Save Data
            interview_form = RoleApplicationInterviewForm(request.POST, instance=application)
            if interview_form.is_valid():
                application = interview_form.save()
                application.application_status = 'interview_invitation'
                application.reviewed_by = request.user.name
                application.save()

                # Get Session
                session = ""
                if application.interview_time_from.hour < 12:
                    session = "SESI PAGI"
                elif application.interview_time_from.hour < 2:
                    session = "SESI TENGAH HARI"
                else:
                    session = "SESI PETANG"

                # Interview Letter
                template_ctx = {
                    'name': application.user.name,
                    'company': application.user.organization,
                    'address1': application.user.address1,
                    'address2': application.user.address2,
                    'postcode': application.user.postcode,
                    'city': application.user.city,
                    'state': application.user.state,
                    'hp_no': application.user.hp_no,
                    'fax_no': application.user.fax_no,
                    'date_now': translate_malay_date(standard_date(datetime.now())),
                    'date': translate_malay_date(standard_date(application.interview_date)),
                    'time_from': application.interview_time_from,
                    'time_to': application.interview_time_to,
                    'location': application.interview_location,
                    'session': session,
                }
                if application.application_type == 'trainer':
                    response = generate_document_file(request, 'trainer_interview_letter', template_ctx, None)
                    application.interview_letter_file.save('pdf', response)
                if application.application_type == 'qca':
                    response = generate_document_file(request, 'qca_interview_letter', template_ctx, None)
                    application.interview_letter_file.save('pdf', response)

                # Email
                to = [application.user.email]
                subject = "Interview Invitation"
                attachments = [application.interview_letter_file]
                email_ctx = {
                    'application': application,
                }
                send_email_with_attachment(subject, to, email_ctx, 'email/role-application-interview.html', attachments)
        
                messages.info(request, 'Successfully invite the applicant for interview session via email.')
        if 'reject' in request.POST:
            application.application_status = 'reject'
            application.reviewed_by = request.user.name
            application.save()

            # Interview Letter
            template_ctx = {
                'name': application.user.name,
                'company': application.user.organization,
                'address1': application.user.address1,
                'address2': application.user.address2,
                'postcode': application.user.postcode,
                'city': application.user.city,
                'state': application.user.state,
                'hp_no': application.user.hp_no,
                'fax_no': application.user.fax_no,
                'date_now': translate_malay_date(standard_date(datetime.now())),
                'date': translate_malay_date(standard_date(application.interview_date)),
                'time_from': application.interview_time_from,
                'time_to': application.interview_time_to,
                'location': application.interview_location,
            }
            if application.application_type == 'trainer':
                response = generate_document_file(request, 'trainer_reject_letter', template_ctx, None)
                application.reject_letter_file.save('pdf', response)
            if application.application_type == 'qca':
                response = generate_document_file(request, 'qca_reject_letter', template_ctx, None)
                application.reject_letter_file.save('pdf', response)

            # Email
            to = [application.user.email]
            subject = "Role Application Result - " + application.get_application_type_display()
            attachments = [application.reject_letter_file]
            email_ctx = {
                'application': application,
            }
            send_email_with_attachment(subject, to, email_ctx, 'email/role-application-reject.html', attachments)
            messages.info(request, 'Successfully sent the rejection letter to applicant via email.')
        
        if 'accreditation' in request.POST:
            assessor_number = ""
            
            if application.application_type == 'trainer':
                trainer, created = Trainer.objects.get_or_create(user=application.user)
                user = application.user
                user.role = 'trainer'
                user.save()
            if application.application_type == 'qca':
                assessor, created = Assessor.objects.get_or_create(user=application.user)
                assessor.assessor_type = 'QCA'
                assessor.save()
                assessor_number = assessor.qca_id
                user = application.user
                user.role = 'assessor'
                user.save()

            application.application_status = 'approved'
            if application.application_type == 'trainer':
                application.accreditation_duration_year = request.POST["accreditation_duration_year"]
                application.accreditation_duration_month = request.POST["accreditation_duration_month"]
            application.save()
            template_ctx = {
                'name': application.user.name,
                'ic': application.user.icno,
                'assessor_number': assessor_number,
                'company': application.user.organization,
                'address1': application.user.address1,
                'address2': application.user.address2,
                'postcode': application.user.postcode,
                'city': application.user.city,
                'state': application.user.state,
                'duration_year': application.accreditation_duration_year,
                'duration_month': application.accreditation_duration_month,
                'hp_no': application.user.hp_no,
                'fax_no': application.user.fax_no,
                'date_now': translate_malay_date(standard_date(datetime.now())),
                'date_accreditation': translate_malay_date(standard_date(datetime.now())),
            }
            if application.application_type == 'trainer':
                # Generate Report
                response_letter = generate_document_file(request, 'trainer_accreditation_letter', template_ctx, None)
                application.accreditation_letter_file.save('pdf', response_letter)
            if application.application_type == 'qca':
                # Generate QR
                qr_path = absoluteuri.build_absolute_uri('/certificate/role-application/'+str(application.id)+'/')
                generate_and_save_qr(qr_path, application.certificate_qr_file)
                # Generate Report
                response_letter = generate_document_file(request, 'qca_accreditation_letter', template_ctx, None)
                response_certificate = generate_document_file(request, 'qca_accreditation_certificate', template_ctx, application.certificate_qr_file)
                application.accreditation_letter_file.save('pdf', response_letter)
                application.accreditation_certificate_file.save('pdf', response_certificate)

            # Email
            to = [application.user.email]
            subject = "Role Application Result - " + application.get_application_type_display()
            attachments = []
            if application.application_type == 'trainer':
                attachments = [application.accreditation_letter_file]
            if application.application_type == 'qca':
                attachments = [application.accreditation_letter_file,application.accreditation_certificate_file]
            email_ctx = {
                'application': application,
            }
            send_email_with_attachment(subject, to, email_ctx, 'email/role-application-accreditation.html', attachments)

            messages.info(request, 'Successfully approved the role application.')

    return render(request, "dashboard/training/role_application_form.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer', 'cidb_reviewer'])
def dashboard_training_list(request):
    mode = 'list'
    trainings = Training.objects.all()
    if request.user.role != 'superadmin' and request.user.role != 'cidb_reviewer':
        trainings = trainings.filter(trainer=request.user)

    context = {
        'title': 'Manage Training',
        'mode': mode,
        'trainings': trainings,
    }
    return render(request, "dashboard/training/manage_training.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer'])
def dashboard_training_new(request):
    mode = 'create'
    training_form = TrainingCreateForm()
    context = {
        'title': 'Add New Training',
        'mode': mode,
        'training_form': training_form,
    }
    if request.method == 'POST':
        training_form = TrainingCreateForm(request.POST)
        if training_form.is_valid():
            training = training_form.save()
            training.trainer = request.user
            training.created_by = request.user.name
            training.save()
            messages.info(request, 'Created successfully')
            return redirect('dashboard_training_update', training.id)
        else:
            messages.warning(request, 'Unable to create new training')
    return render(request, "dashboard/training/manage_training.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer'])
def dashboard_training_update(request, id):
    mode = 'update'
    training = get_object_or_404(Training, id=id)
    training_form = TrainingCreateForm(instance=training)
    coaches = Coach.objects.all().filter(training=training)
    coach_form = CoachCreateForm()
    context = {
        'title': 'Update Training',
        'mode': mode,
        'training_form': training_form,
        'coach_form': coach_form,
        'training': training,
        'coaches':coaches,
    }

    if request.method == 'POST':
        if 'update_training' in request.POST:
            training_form = TrainingCreateForm(request.POST, instance=training)
            if training_form.is_valid():
                form = training_form.save()
                form.modified_by = request.user.name
                form.save()
                messages.info(request, 'Updated successfully')
            else:
                messages.warning(request, 'Unable to update training')
        if 'create_coach' in request.POST:
            coach_form = CoachCreateForm(request.POST)
            if coach_form.is_valid():
                form = coach_form.save()
                form.training = training
                form.created_by = request.user.name
                form.save()
                messages.info(request, 'Added successfully')
            else:
                messages.warning(request, 'Unable to add new coach:'+coach_form.errors.as_text())
        return redirect('dashboard_training_update', training.id)
    return render(request, "dashboard/training/manage_training.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer'])
def dashboard_training_review(request, id):
    mode = 'review'
    training = get_object_or_404(Training, id=id)
    training_form = TrainingCreateForm(instance=training)
    coaches = Coach.objects.all().filter(training=training)
    coach_form = CoachCreateForm()
    context = {
        'title': 'Review Training',
        'mode': mode,
        'training_form': training_form,
        'coach_form': coach_form,
        'training': training,
        'coaches': coaches,
    }

    if request.method == 'POST':
        if 'reject' in request.POST:
            training.review_status = 'rejected'
            training.save()
            messages.info(request, 'Rejected successfully')
        if 'accept' in request.POST:
            training.review_status = 'accepted'
            training.save()
            messages.info(request, 'Accept successfully')
        return redirect('dashboard_training_list')
    return render(request, "dashboard/training/manage_training.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer'])
def dashboard_training_coach_update(request, id):
    coach = get_object_or_404(Coach, id=id)
    training = coach.training
    coach_form = CoachCreateForm(instance=coach)
    context = {
        'title': 'Manage Coach',
        'training': training,
        'coach_form': coach_form,
    }

    if request.method == 'POST':
        if 'update' in request.POST:
            coach_form = CoachCreateForm(request.POST, instance=coach)
            if coach_form.is_valid():
                form = coach_form.save()
                form.modified_by = request.user.name
                form.save()
                messages.info(request, 'Updated successfully')
            else:
                messages.warning(request, 'Unable to update coach information')
        if 'delete' in request.POST:
            training_id = coach.training.id
            coach.delete()
            messages.info(request, 'Delete successfully')
            return redirect('dashboard_training_update', training_id)
        return redirect('dashboard_training_coach_update', coach.id)
    return render(request, "dashboard/training/coach_form.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer', 'cidb_reviewer', 'applicant', 'trainee'])
def dashboard_available_training_list(request):
    mode = 'all'
    trainings = Training.objects.all().filter(review_status='accepted')
    registration_trainings = RegistrationTraining.objects.all().filter(user=request.user).order_by('-created_date')
    filtered_trainings = []
    for tr in trainings:
        tr_dict = {
            'id': tr.id,
            'training_name': tr.training_name,
            'training_type': tr.training_type,
            'fee': tr.fee,
            'from_date': tr.from_date,
            'to_date': tr.to_date,
            'current_pax': tr.current_pax(),
            'size': tr.size,
            'review_status': tr.get_attendance_review_status_display,
            'is_available': True,
            'is_registered': False,
            'is_end': False,
        }
        for rt in registration_trainings:
            if rt.training == tr:
                if rt.status=="accepted" or rt.status=='need_payment':
                    tr_dict['is_available'] = False
                    tr_dict['is_registered'] = True
                    break 
        if tr.attendance_review_status == 'approved':
            tr_dict['is_end'] = True
        else:
            if tr_dict['is_available'] == True:
                if tr.is_available() == False:
                    tr_dict['is_available'] = False
        filtered_trainings.append(tr_dict)
                    

    context = {
        'title': 'Available Training List',
        'mode': mode,
        'trainings': filtered_trainings,
    }
    return render(request, "dashboard/training/enroll_training.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer', 'applicant', 'trainee'])
def dashboard_joined_training_list(request):
    mode = 'joined_training'
    trainings = RegistrationTraining.objects.all().filter(user=request.user)
    context = {
        'title': 'Joined Training',
        'mode': mode,
        'trainings': trainings,
        'payment_history_url':get_payment_history_url(request),
    }
    return render(request, "dashboard/training/enroll_training.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'applicant', 'trainee'])
def dashboard_joined_training_pay(request, id):
    mode = 'payment'
    rt = get_object_or_404(RegistrationTraining, id=id)
    training = rt.training
    response = create_training_transaction(request, training.fee, 'YKSHEQ', 'YURAN KURSUS', rt.code_id, request.user)
    proforma = response.Code
    print(str(response))
    
    response_url = get_domain(request) + '/dashboard/training/joined/payment/'+id+'/response/'


    # Create Payment
    payment, created = Payment.objects.get_or_create(order_id=proforma)
    payment.user = request.user
    payment.customer_name = request.user.name
    payment.customer_email = request.user.email
    payment.rt = rt
    payment.currency = 'MYR'
    payment.payment_amount = response.Amount
    payment.save()

    context = {
        'title': 'Payment - Joined Training',
        'mode': mode,
        'training': rt,
        'amount': payment.payment_amount,
        'proforma': proforma,
        'response': response,
        'url': payment_gateway_url,
        'response_url': response_url,
    }
    return render(request, "dashboard/training/enroll_training.html", context)

@csrf_exempt
def dashboard_joined_training_pay_response(request, id):
    mode = 'payment_response'
    payment = None
    rt = get_object_or_404(RegistrationTraining, id=id)
    if request.method == 'POST':
        payment = payment_response_process(request)
        if payment != None:
            rt.payment_status = payment.payment_status
            rt.save()
            if payment.payment_status == 1:
                rt.status = 'accepted'
                rt.save()
            elif payment.payment_status == 2:
                messages.info(request, payment.status_description)
                rt.status = 'pending'
                rt.save()
            else:
                messages.warning(request, payment.status_description)
        else:
            messages.warning(request, 'Problem with processing the transaction. Please contact with our staff to verify the transaction.')
    
    receipt_url = None
    if payment != None:
        receipt_url = get_receipt_url + payment.order_id

    context = {
        'title': 'Payment Response - Joined Training',
        'mode': mode,
        'training': rt,
        'receipt_url': receipt_url,
        'payment': payment,
    }
    return render(request, "dashboard/training/enroll_training.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer', 'trainer', 'applicant', 'trainee'])
def dashboard_training_participant(request, id):
    mode = 'participant'
    training = get_object_or_404(Training, id=id)
    available_seat, is_available = check_available_seat(request, training)
    participants = RegistrationTraining.objects.all().filter(training__id = id)
    context = {
        'title': 'List of Participant',
        'mode': mode,
        'participants': participants,
        'training': training,
        'available_seat': available_seat,
        'is_available': is_available,
    }
    return render(request, "dashboard/training/enroll_training.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer'])
def dashboard_training_participant_review(request, id):
    mode = 'participant_review'
    rt = get_object_or_404(RegistrationTraining, id=id)
    training = rt.training
    form_review = RegistrationTrainingReviewForm()
    available_seat, is_available = check_available_seat(request, training)
    context = {
        'title': 'Participant Review',
        'mode': mode,
        'rt': rt,
        'training': training,
        'available_seat': available_seat,
        'is_available': is_available,
        'form_review': form_review,
    }
    if request.method == 'POST':
        if 'accept' in request.POST:
            form_review = RegistrationTrainingReviewForm(request.POST, instance=rt)
            if form_review.is_valid():
                form = form_review.save()
                form.reviewed_by = request.user.name
                
                if form.payment_mode == 'on':
                    form.status = 'need_payment'
                else:
                    form.status = 'accepted'
                    form.payment_status = -2
                form.save()
                messages.info(request, 'Accepted the participant successfully')

                # Email
                to = []
                to.append(rt.user.email)
                subject = "Request to Join Training - " + rt.code_id + " (" + training.training_name + ")"
                ctx_email = {
                    'training':training,
                    'rt': rt,
                }
                send_email_default(subject, to, ctx_email, 'email/training-join-response.html')

            else:
                messages.warning(request, 'Unable to review the participant')
        if 'reject' in request.POST:
            form_review = RegistrationTrainingReviewForm(request.POST, instance=rt)
            if form_review.is_valid():
                form = form_review.save()
                form.reviewed_by = request.user.name
                form.status = 'rejected'
                form.save()
                messages.info(request, 'Rejected the participant successfully')

                  # Email
                to = []
                to.append(rt.user.email)
                subject = "Request to Join Training - " + rt.code_id + " (" + training.training_name + ")"
                ctx_email = {
                    'training':training,
                    'user': rt.user,
                }
                send_email_default(subject, to, ctx_email, 'email/training-join-response.html')
            else:
                messages.warning(request, 'Unable to review the participant')
        return redirect('dashboard_training_participant', training.id)
    return render(request, "dashboard/training/enroll_training.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainee', 'applicant'])
def dashboard_training_join(request, id):
    training = get_object_or_404(Training, id=id)
    existing = RegistrationTraining.objects.all().filter(training=training, user=request.user).order_by('-created_date')
    if len(existing) > 0:
        current = existing[0]
        if current.status == 'pending':
            messages.warning(request, 'Unable to register the training. You already applied this training. Please wait for the approval.')
            return redirect('dashboard_available_training_list')
        elif current.status == 'accepted':
            messages.warning(request, 'Unable to register the training. You have been accepted to join this training.')
            return redirect('dashboard_available_training_list')
        elif current.status == 'need_payment':
            messages.warning(request, 'Unable to register the training. You already applied this training. Please proceed with the payment.')
            return redirect('dashboard_available_training_list')
        else:
            pass

    available_seat, is_available = check_available_seat(request, training)
    mode = 'register'
    # print(type(ORGANIZATION_TYPE_CHOICES))
    context = {
        'title': 'Join Training',
        'mode': mode,
        'organization_type_choices': ORGANIZATION_TYPE_CHOICES,
        'training': training,
        'available_seat': available_seat,
        'is_available': is_available,
    }

    if request.method == 'POST':
        rt = RegistrationTraining.objects.create(training=training, user=request.user)
        rt.participant_name = request.user.name
        rt.participant_icno = request.user.icno
        rt.participant_email = request.user.email
        rt.participant_hpno = request.user.hp_no
        rt.participant_organization = request.user.organization
        rt.participant_organization_type = request.POST['participant_organization_type']
        rt.participant_designation = request.POST['participant_designation']
        rt.save()

        # Email
        cidb_reviewers = CustomUser.objects.all().filter(
            Q(role='cidb_reviewer')|
            Q(role='superadmin')
        )
        to = []
        for reviewer in cidb_reviewers:
            to.append(reviewer.email)
        subject = "Request to Join Training - " + rt.code_id + " (" + training.training_name + ")"
        ctx_email = {
            'training':training,
        }
        send_email_default(subject, to, ctx_email, 'email/training-join-request.html')

        messages.warning(request, 'Successfully request to join the training. Please wait for approval from reviewer before proceeding with payment.')
        return redirect('dashboard_joined_training_list')

    return render(request, "dashboard/training/enroll_training.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer'])
def dashboard_training_attendance_trainer(request, id):
    training = get_object_or_404(Training, id=id)
    attendances = RegistrationTraining.objects.all().filter(training=training, status='accepted')
    attendance_sheet_form = AttendanceSheetUploadForm(instance=training)
    mode = 'trainer'
    context = {
        'attendance_sheet_form': attendance_sheet_form,
        'title': 'Mark Attendance List - ' + training.training_name,
        'mode': mode,
        'training': training,
        'attendances': attendances,
    }
    if request.method == 'POST':
        if 'upload_attendance_sheet' in request.POST:
            attendance_sheet_form = AttendanceSheetUploadForm(request.POST, request.FILES, instance=training)
            attendance_sheet_form.save()
            messages.info(request, 'Successfully upload the attendance sheet.')
        elif 'approval' in request.POST:
            if training.attendance_sheet_file != '':
                training.attendance_review_status = 'need_approval'
                training.save()
                messages.info(request, 'Successfully send the attendance for approval.')
            else:
                messages.warning(request, 'You must upload the attendance sheet file before sending the attendance for approval.')
        elif 'generate_template' in request.POST:
            trainers = Coach.objects.all().filter(training=training)
            venue = training.address1 + ', ' + training.address2 + ', ' + training.postcode + ' ' + training.city + ', ' + training.state
            tmpl_ctx = {
                'training_name': training.training_name,
                'trainers': trainers,
                'venue': venue,
                'days': range(training.number_of_days()),
                'from_date': translate_malay_date(standard_date(training.from_date)),
                'to_date': translate_malay_date(standard_date(training.to_date)),
                'from_time': training.from_time,
                'to_time': training.to_time,
                'participants': attendances,
            }
            response = generate_document(request, 'attendance_sheet', tmpl_ctx)
            return response 
        else:
            participant_id = request.POST['id']
            rt = RegistrationTraining.objects.get(id=participant_id)
            if 'attend_full' in request.POST:
                rt.attendance_full = True
                rt.save()
                messages.info(request, 'Changed attendance as FULL')
            if 'attend_not_full' in request.POST:
                rt.attendance_full = False
                rt.save()
                messages.info(request, 'Changed attendance as NOT FULL')
            if 'mark' in request.POST:
                rt.marks = request.POST['marks']
                rt.save()
                messages.info(request, 'Changed marks')
        return redirect('dashboard_training_attendance_trainer', training.id)

    return render(request, "dashboard/training/attendance.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer'])
def dashboard_training_attendance_review(request, id):
    training = get_object_or_404(Training, id=id)
    attendances = RegistrationTraining.objects.all().filter(training=training, status='accepted')
    mode = 'reviewer'
    context = {
        'title': 'Review Attendance List - ' + training.training_name,
        'mode': mode,
        'training': training,
        'attendances': attendances,
    }

    if request.method == 'POST':
        if 'generate' in request.POST:
            for attendance in attendances:
                if attendance.attendance_full == True:
                    if training.cert_type == 'pass':
                        if attendance.marks >= training.passing_mark:
                            attendance.pass_status = True
                        else:
                            attendance.pass_status = False
                    else:
                        attendance.pass_status = True
                else:
                    attendance.pass_status = False
                
                generate_pdf = False

                if attendance.pass_status == True:
                    generate_pdf = True
                else:
                    if training.cert_type == 'pass':
                        generate_pdf = True
                    
                if generate_pdf == True:
                    pass_status = ""
                    training_location = training.address1 + ' ' + training.address2 + ', ' + training.postcode + ' ' + training.city + ', ' + training.state
                    # Check if PASS or FAIL
                    if attendance.pass_status == True:
                        pass_status = 'LULUS'
                    else:
                        pass_status = 'GAGAL'
                    
                    # Set training date display
                    training_date = None
                    if training.from_date == training.to_date:
                        training_date = translate_malay_date(standard_date(training.from_date))
                    else:
                        training_date = translate_malay_date(standard_date(training.from_date)) + ' - ' + translate_malay_date(standard_date(training.to_date))
                    
                    template_ctx = {
                        'pass': pass_status,
                        'name': attendance.user.name,
                        'hp_no': attendance.user.hp_no,
                        'fax_no': attendance.user.fax_no,
                        'ic': attendance.user.icno,
                        'address1': attendance.user.address1,
                        'address2': attendance.user.address2,
                        'postcode': attendance.user.postcode,
                        'city': attendance.user.city,
                        'state': attendance.user.state,
                        'company': attendance.user.organization,
                        'location': training_location,
                        'date_now': translate_malay_date(standard_date(datetime.now())),
                        'date': training_date,
                    }
                    response = generate_training_document_file(request, training.training_type, template_ctx, None)
                    attendance.certificate_file.save('pdf', response)

                attendance.save()
            messages.info(request, 'Successfully generated the document for participants.')  
        if 'approve' in request.POST:
            training.attendance_review_status = 'approved'
            training.save()

            training_types = TrainingType.objects.all().filter(required_for_assessor=True)

            # Email
            for attendance in attendances:
                
                # Check Eligible for QIA
                qia_eligible = True
                all_trainings = RegistrationTraining.objects.all().filter(user=attendance.user)
                if len(all_trainings) > 1:
                    for training_type in training_types:
                        found = False
                        for all_training in all_trainings:
                            if training_type == all_training.training.training_type:
                                found = True
                                break
                        if found == False:
                            qia_eligible = False
                            break
                else:
                    qia_eligible = False

                if qia_eligible == True:
                    user = attendance.user
                    user.qia_status = 'need_review'
                    user.save()  

                    # Email
                    cidb_reviewers = CustomUser.objects.all().filter(
                        Q(role='superadmin')|
                        Q(role='cidb_reviewer')
                    )
                    to = []
                    for cidb_reviewer in cidb_reviewers:
                        to.append(cidb_reviewer.email)

                    subject = "Request for QIA Certificate - " + attendance.code_id
                    email_ctx = {
                        'attendance': attendance,
                    }
                    send_email_default(subject, to, email_ctx, 'email/training-qia-review.html')
                
                # Email
                to = [attendance.user.email]
                subject = "Training Certificate - " + training.training_name
                attachments = [attendance.certificate_file]
                email_ctx = {
                    'training': training,
                    'attendance': attendance,
                }
                send_email_with_attachment(subject, to, email_ctx, 'email/training-certificate.html', attachments)



            messages.info(request, 'Successfully approved the attendance.')
        return redirect('dashboard_training_attendance_review', training.id)

    return render(request, "dashboard/training/attendance.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['trainee', 'applicant'])
def dashboard_training_feedback_list_trainee(request):
    feedbacks = Feedback.objects.all().filter(user=request.user)

    context = {
        'role': 'trainee',
        'feedbacks':feedbacks,
    }

    return render(request, "dashboard/training/feedback_list.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer'])
def dashboard_training_feedback_list_staff(request):
    feedbacks = Feedback.objects.all()

    context = {
        'role': 'staff',
        'feedbacks':feedbacks,
    }

    return render(request, "dashboard/training/feedback_list.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['trainee', 'applicant'])
def dashboard_training_feedback_application(request, id):
    training = get_object_or_404(Training, id=id)
    context = {
        'training':training,
    }

    if request.method == 'POST':
        form = FeedbackCreateForm(request.POST)
        if form.is_valid():
            data = form.save()
            data.user = request.user
            data.training = training
            data.save()
            messages.info(request, 'Successfully send the feedback.')
            return redirect('dashboard_joined_training_list')
        else:
            messages.warning(request, 'Problem with sending the feedback.')
            return redirect('dashboard_training_feedback_application', training.id)

    return render(request, "dashboard/training/feedback_application.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer'])
def dashboard_training_feedback_review(request, id):
    feedback = get_object_or_404(Feedback, id=id)
    trainers = Coach.objects.all().filter(training=feedback.training)
    print(len(trainers))
    mode = 'review'
    context = {
        'mode': mode,
        'feedback':feedback,
        'trainers':trainers,
    }

    if request.method == 'POST':
        feedback.warning = request.POST['warning']
        feedback.warning_delivered = True
        feedback.warning_delivered_date = datetime.now()
        feedback.reviewer = request.user
        feedback.save()

        # Email
        to = []
        for trainer in trainers:
            to.append(trainer.email)
        subject = "Complaint From Trainee - " + feedback.training.training_name
        ctx_email = {
            'feedback':feedback,
        }
        messages.info(request, 'Successfully delivered an email to trainer(s).')
        send_email_default(subject, to, ctx_email, 'email/training-complaint.html')
           
        return redirect('dashboard_training_feedback_review', feedback.id)

    return render(request, "dashboard/training/feedback_application.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer', 'trainee', 'applicant', 'trainer', 'assessor'])
def dashboard_joined_training_certificate(request):
    trainings = RegistrationTraining.objects.all().filter(user=request.user, pass_status=True)
    assessor_all = Assessor.objects.all().filter(user=request.user)
    assessor = None
    if len(assessor_all) > 0:
        assessor = assessor_all[0]
    context = {
        'title': 'Training Certificate List',
        'mode': 'trainee',
        'trainings':trainings,
        'assessor': assessor,
        'user': request.user,
        'payment_history_url':get_payment_history_url(request),
    }

    return render(request, "dashboard/training/certificate_list.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer'])
def dashboard_qia_application_list(request):
    users = CustomUser.objects.all().filter(qia_status='need_review')
    context = {
        'title': 'QLASSIC Industry Assessor Candidates',
        'mode': 'list',
        'users':users,
    }
    return render(request, "dashboard/training/qia_application.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'cidb_reviewer'])
def dashboard_qia_application_review(request, id):
    user = get_object_or_404(CustomUser, id=id, qia_status='need_review')
    trainings = RegistrationTraining.objects.all().filter(user=user, pass_status=True)

    context = {
        'title': 'QIA Candidate Review',
        'mode': 'review',
        'trainings':trainings,
        'user': user,
    }

    if request.method == 'POST':
        user.qia_status = 'need_payment'
        user.save()

        to = [user.email]
        subject = "Payment for QLASSIC Industry Assessor Certificate"
        email_ctx = {
            'user': user,
        }
        send_email_default(subject, to, email_ctx, 'email/training-qia-payment.html')

        messages.info(request, 'Successfully notify the trainee to make payment.')
        return redirect('dashboard_qia_application_list')
    return render(request, "dashboard/training/certificate_list.html", context)


@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin', 'trainer', 'assessor', 'trainee', 'applicant'])
def dashboard_qia_application_pay(request, id):
    mode = 'payment'
    user = get_object_or_404(CustomUser, id=id)
    response = create_transaction(request, 1, 'QLC-PUP', 'PENTAULIAHAN QIA','QIA-'+user.code_id, request.user)
    proforma = response.Code

    response_url = get_domain(request) + '/dashboard/training/qia/application/payment/'+id+'/response/'
    
    # Create Payment
    payment, created = Payment.objects.get_or_create(order_id=proforma)
    payment.user = request.user
    payment.customer_name = request.user.name
    payment.customer_email = request.user.email
    payment.currency = 'MYR'
    payment.payment_amount = response.Amount
    payment.save()

    context = {
        'title': 'Payment - QLASSIC Industry Assessor Certificate',
        'mode': mode,
        'user': user,
        'proforma': proforma,
        'amount': response.Amount,
        'response': response,
        'url': payment_gateway_url,
        'response_url': response_url,
    }
    return render(request, "dashboard/training/qia_application.html", context)

@csrf_exempt
def dashboard_qia_application_pay_response(request, id):
    mode = 'payment_response'
    payment = None
    user = get_object_or_404(CustomUser, id=id)
    if request.method == 'POST':
        payment = payment_response_process(request)
        if payment != None:
            if payment.payment_status == 1:
                user.qia_status = 'accepted'
                user.save()
                assessor, created = Assessor.objects.get_or_create(user=user)
                assessor.assessor_type = 'QIA'
                assessor.save()
                # Generate QR
                qr_path = absoluteuri.build_absolute_uri('/certificate/qia/'+str(user.id)+'/')
                generate_and_save_qr(qr_path, assessor.qia_certificate_qr_file)

                # Cert Generation
                template_ctx = {
                    'name': user.name,
                    'ic': user.icno,
                    'assessor_number': assessor.qia_id,
                    'date_accreditation': translate_malay_date(standard_date(datetime.now())),
                }
                response = generate_document_file(request, 'qia_accreditation_certificate', template_ctx, assessor.qia_certificate_qr_file)
                assessor.qia_certificate_file.save('pdf', response)
                
                # Email
                to = [user.email]
                subject = "QLASSIC Industry Application Successful"
                attachments = [assessor.qia_certificate_file]
                email_ctx = {
                    'assessor': assessor,
                    'user': user,
                }
                send_email_with_attachment(subject, to, email_ctx, 'email/training-qia-accreditation.html', attachments)

                messages.info(request, 'You are successfully certified as QLASSIC Industry Assessor.')
            else:
                messages.warning(request, payment.status_description)
        else:
            messages.warning(request, 'Problem with processing the transaction. Please contact with our staff to verify the transaction.')
    
    receipt_url = None
    if payment != None:
        receipt_url = get_receipt_url + payment.order_id
    
    context = {
        'title': 'Payment Response - QLASSIC Industry Assessor Certificate',
        'mode': mode,
        'user': user,
        'receipt_url': receipt_url,
        'payment': payment,
    }
    return render(request, "dashboard/training/qia_application.html", context)


## AJAX
@login_required(login_url="/login/")
def ajax_api_training_payment_request(request):
    if request.method == 'POST':
        id = request.POST['id']
        
        rt = get_object_or_404(RegistrationTraining, id=id)
        training = rt.training
        response = create_training_transaction(request, training.fee, 'YKSHEQ', 'YURAN KURSUS QLASSIC', rt.code_id, request.user)
        # response = create_transaction(request, 1, 'QLC-PUP', 'YURAN KURSUS QLASSIC', rt.code_id, request.user)
        
        proforma = response.Code
        payment, created = Payment.objects.get_or_create(order_id=proforma)
        if created == False:
            if payment.payment_amount != response.Amount:
                cancel_proforma(proforma)
                response = create_training_transaction(request, training.fee, 'YKSHEQ', 'YURAN KURSUS QLASSIC', rt.code_id, request.user)
                proforma = response.Code
                payment, created = Payment.objects.get_or_create(order_id=proforma)

        # Create Payment
        payment.user = request.user
        payment.customer_name = request.user.name
        payment.customer_email = request.user.email
        payment.rt = rt
        payment.currency = 'MYR'
        payment.payment_amount = response.Amount
        payment.save()

        result = response.TransactionResult
        error = response.ErrorMessage
        print(str(response))
        response_url = get_domain(request) + '/dashboard/training/joined/payment/'+id+'/response/'
        postdata = {
            'payment_gateway_url':payment_gateway_url,
            'ClientReturnURL':response_url,
            'IcOrRoc':request.user.code_id,
            'OrderID':proforma,
            'Currency':"MYR",
            'TransactionType':"SALE",
            'ClientRef0':"",
            'ClientRef1':"",
            'ClientRef2':"",
            'ClientRef3':"",
            'ClientRef4':"",
            'Amount': payment.payment_amount,
            'CustomerName':request.user.name,
            'CustomerEmail':request.user.email,
            'CustomerPhoneNo':request.user.hp_no,
            'result':result,
            'error':error,
        }

        return JsonResponse(postdata)
    else:
        return JsonResponse({})

@login_required(login_url="/login/")
def ajax_api_qia_payment_request(request):
    if request.method == 'POST':
        id = request.POST['id']
        
        user = get_object_or_404(CustomUser, id=id)
        response = create_transaction(request, 1, 'QLC-PUP', 'PENTAULIAHAN QIA','QIA-'+user.code_id, request.user)
        proforma = response.Code
        payment, created = Payment.objects.get_or_create(order_id=proforma)
        if created == False:
            if payment.payment_amount != response.Amount:
                cancel_proforma(proforma)
                response = create_transaction(request, 1, 'QLC-PUP', 'PENTAULIAHAN QIA','QIA-'+user.code_id, request.user)
                proforma = response.Code
                payment, created = Payment.objects.get_or_create(order_id=proforma)
        
        # Create Payment
        payment.user = request.user
        payment.customer_name = request.user.name
        payment.customer_email = request.user.email
        payment.currency = 'MYR'
        payment.payment_amount = response.Amount
        payment.save()

        result = response.TransactionResult
        error = response.ErrorMessage
        response_url = get_domain(request) + '/dashboard/training/qia/application/payment/'+id+'/response/'
        postdata = {
            'payment_gateway_url':payment_gateway_url,
            'ClientReturnURL':response_url,
            'IcOrRoc':request.user.code_id,
            'OrderID':proforma,
            'Currency':"MYR",
            'TransactionType':"SALE",
            'ClientRef0':"",
            'ClientRef1':"",
            'ClientRef2':"",
            'ClientRef3':"",
            'ClientRef4':"",
            'Amount': payment.payment_amount,
            'CustomerName':request.user.name,
            'CustomerEmail':request.user.email,
            'CustomerPhoneNo':request.user.hp_no,
            'result':result,
            'error':error,
        }

        return JsonResponse(postdata)
    else:
        return JsonResponse({})
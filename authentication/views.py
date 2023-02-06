# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from django.contrib import messages

# SendMail Sendgrid
from django.core.mail import send_mail

# Activate Account Related
from django.views.generic import View
from django.utils.encoding import force_text, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.sites.shortcuts import get_current_site

from users.models import CustomUser

# def login_view(request):
#     form = LoginForm(request.POST or None)

#     msg = None

#     if request.method == "POST":

#         if form.is_valid():
#             username = form.cleaned_data.get("username")
#             password = form.cleaned_data.get("password")
#             user = authenticate(username=username, password=password)
#             if user is not None:
#                 login(request, user)
#                 return redirect("/")
#             else:    
#                 msg = 'Invalid credentials'    
#         else:
#             msg = 'Error validating the form'    

#     return render(request, "accounts/login.html", {"form": form, "msg" : msg})

def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request,'Login Successfully')
                if user.role == 'superadmin':
                    return redirect("/")
                else:
                    return redirect('dashboard')
            else:    
                user = CustomUser.objects.all().filter(email=email)
                if len(user) > 0:
                    if user[0].is_active == False:
                        messages.warning(request,'Please activate your account by clicking the activation link sent to this registered email. It may require you to check the spam email.')  
                    else:
                        messages.warning(request,'Invalid credentials')  
                else:
                    messages.warning(request,'Invalid credentials')  
                return redirect("/")
        else:
            messages.warning(request,'Error validating the form')   

    return render(request, "index.html", {"msg" : msg})

# def register_user(request):

#     msg     = None
#     success = False

#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get("username")
#             raw_password = form.cleaned_data.get("password1")
#             user = authenticate(username=username, password=raw_password)

#             msg     = 'User created - please <a href="/login">login</a>.'
#             success = True
            
#             #return redirect("/login/")

#         else:
#             msg = 'Form is not valid'    
#     else:
#         form = SignUpForm()

#     return render(request, "accounts/register.html", {"form": form, "msg" : msg, "success" : success })

def register_user(request):

    msg     = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=email, password=raw_password)
            user.is_active = False
            user.save()
            
            # Email
            current_site = get_current_site(request)
            subject = 'Activate Your QLASSIC Account'
            message = render_to_string('email/activate-account.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)

            messages.success(request, 'Registered successfully. Please check your email in order to complete the registration.')
            success = True
            
            return redirect('dashboard_profile')
        else:
            messages.warning(request, 'Form is not valid')
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "success" : success })

class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, ('Congratulation! Your account have been activated.'))
            return redirect('home')
        else:
            #messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
            user.is_active = True
            user.save()
            login(request, user)
            messages.success(request, ('Congratulation! Your account have been activated.'))
            return redirect('home')

# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.models import CustomUser

class LoginForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder" : "Email",                
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))

# class SignUpForm(UserCreationForm):
#     username = forms.CharField(
#         widget=forms.TextInput(
#             attrs={
#                 "placeholder" : "Identity Card Number",                
#                 "class": "form-control"
#             }
#         ))
#     email = forms.EmailField(
#         widget=forms.EmailInput(
#             attrs={
#                 "placeholder" : "Email",                
#                 "class": "form-control"
#             }
#         ))
#     password1 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 "placeholder" : "Password",                
#                 "class": "form-control"
#             }
#         ))
#     password2 = forms.CharField(
#         widget=forms.PasswordInput(
#             attrs={
#                 "placeholder" : "Confirm Password",                
#                 "class": "form-control"
#             }
#         ))

#     class Meta:
#         model = User
#         fields = ('username', 'email', 'password1', 'password2')

class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder" : "Email",                
                "class": "form-control"
            }
        ))
    # role = forms.ChoiceField(
    #     choices =[
    #         # To follow SRS
    #         ('contractor','Contractor'),
    #         ('trainee','Trainee'),
    #         ('applicant','Applicant'),
    #         ('staff','Staff'),
    #     ],
    #     label = "I want to use the system as a"
    # )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Password",                
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder" : "Confirm Password",                
                "class": "form-control"
            }
        ))

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

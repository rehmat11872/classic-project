# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import Http404
import datetime
import random

# Forms
from users.forms import RoleUpdateForm
# Models
from users.models import Assessor, CustomUser, Trainer

# Decorators
from authentication.decorators import allowed_users
from django.db.models import Q

### Admin - Application Module ###
@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_management_user(request):
    users = CustomUser.objects.all()
    role = ''
    if 'role' in request.GET:
        role = request.GET['role']
        if role != '':
            if role == 'all':
                pass
            elif role == 'none':
                users = users.filter(
                    Q(role='')|
                    Q(role=None)
                )
            else:
                users = users.filter(role=role)
    context = {
        'users':users,
        'role':role,
    }
    return render(request, "dashboard/management/user.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_management_user_id(request, id):
    user = get_object_or_404(CustomUser, id=id)
    role_form = RoleUpdateForm(instance=user)
    context = {
        'role_form':role_form,
        'user':user,
    }

    if request.method == "POST":
        if 'update' in request.POST:
            role_form = RoleUpdateForm(request.POST, instance=user)
            if role_form.is_valid():
                role_form.save()
                messages.info(request, 'Successfully updated the role of user')
            else:
                messages.warning(request, 'Error updating the role of user')
        if 'assessor' in request.POST:
            assessor, created = Assessor.objects.get_or_create(user=user)
            messages.info(request, 'Successfully approved as an assessor')
        if 'trainer' in request.POST:
            trainer, created = Trainer.objects.get_or_create(user=user)
            messages.info(request, 'Successfully approved as a trainer')
        return redirect('dashboard_management_user_id', user.id)

    return render(request, "dashboard/management/user_id.html", context)

@login_required(login_url="/login/")
@allowed_users(allowed_roles=['superadmin'])
def dashboard_management_user_id_delete(request, id):
    #user = get_object_or_404(CustomUser, id=id)
    #user.delete()
    return redirect('dashboard_management_user')

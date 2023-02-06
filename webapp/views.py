from django.shortcuts import render

# Create your views here.

# @allowed_users(allowed_roles=['superadmin', 'trainer'])
# @login_required(login_url="/login/")
def webapp_home(request):
    context = {
    }
    return render(request, "webapp/home.html", context)

def webapp_login(request):
    context = {
    }
    return render(request, "webapp/login.html", context)
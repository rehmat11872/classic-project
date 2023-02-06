from django.contrib import admin

from .models import *
# Register your models here.
admin.site.register(Training)
admin.site.register(RegistrationTraining)
admin.site.register(TrainingType)
admin.site.register(Coach)
admin.site.register(RoleApplication)
admin.site.register(Feedback)
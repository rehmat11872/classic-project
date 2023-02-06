from django.contrib import admin
from .models import Announcement, LetterTemplate, Publication, Training,UpdateInformation
# Register your models here.
admin.site.register(Announcement)
admin.site.register(Publication)
# admin.site.register(Training)
admin.site.register(LetterTemplate)
admin.site.register(UpdateInformation)
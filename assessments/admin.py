from django.contrib import admin
from .models import *
# Register your models here.

class QAAAdmin(admin.ModelAdmin):
    list_display = ('qaa_number', 'user', 'application_status', 'created_date','modified_date',)

class SDAdmin(admin.ModelAdmin):
    list_display = ('qaa', 'file_name', 'created_date','modified_date',)

class ComponentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code_id', 'created_date')

class SampleResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'test_type', 'element_code', 'created_date')

class SyncResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'qaa', 'result', 'sync_complete', 'created_date')

class ElementResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'qaa', 'result', 'element_code', 'dg_name', 'created_date')

class AssignedAssessorAdmin(admin.ModelAdmin):
    list_display = ('id', 'assessor', 'ad', 'role_in_assessment', 'complete', 'created_date')

admin.site.register(QlassicAssessmentApplication, QAAAdmin)
admin.site.register(SupportingDocuments, SDAdmin)
admin.site.register(SuggestedAssessor)
admin.site.register(AssignedAssessor, AssignedAssessorAdmin)
admin.site.register(AssessmentData)
admin.site.register(WorkCompletionForm)
admin.site.register(QlassicReporting)
admin.site.register(SampleResult, SampleResultAdmin)
admin.site.register(ElementResult, ElementResultAdmin)
admin.site.register(SyncResult, SyncResultAdmin)
admin.site.register(Component,ComponentAdmin)
admin.site.register(SubComponent,ComponentAdmin)
admin.site.register(Element,ComponentAdmin)
admin.site.register(DefectGroup,ComponentAdmin)
admin.site.register(SiteAttendance)
admin.site.register(Survey)
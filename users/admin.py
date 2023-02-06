from django.contrib import admin
from .models import CustomUser, Assessor, Trainer
from .forms import CustomUserCreationForm, CustomUserChangeForm
from django.contrib.auth.admin import UserAdmin

# Register your models here.
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_active','code_id')
    list_filter = ('email', 'is_staff', 'is_active',)
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'code_id')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'role', 'name', 'icno', 'state', 'qia_status')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Trainer)
admin.site.register(Assessor)
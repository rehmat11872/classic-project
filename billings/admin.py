from billings.models import ClaimApplication
from django.contrib import admin

from .models import ClaimApplication, Payment

# Register your models here.
admin.site.register(ClaimApplication)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('code_id', 'order_id', 'proforma_cancelled', 'payment_amount', 'payment_status','created_date')
admin.site.register(Payment, PaymentAdmin)
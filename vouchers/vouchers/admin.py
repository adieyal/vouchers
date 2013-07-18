from django.contrib import admin
from django.contrib.admin import filters
import models

class VoucherAdmin(admin.ModelAdmin):
    list_filter = ("network", "allocated")
    list_display = ("network", "voucher_number1", "voucher_number2", "allocated", "allocation_date")

class SurveyAllocationAdmin(admin.ModelAdmin):
    list_display = ("survey_id", "voucher", 'is_used')

admin.site.register(models.Voucher, VoucherAdmin)
admin.site.register(models.SurveyAllocation, SurveyAllocationAdmin)

from django.contrib import admin
import models

class VoucherAdmin(admin.ModelAdmin):
    list_filter = ("network", "allocated")
    list_display = ("network", "survey_id", "voucher_number", "allocated")

admin.site.register(models.Voucher, VoucherAdmin)

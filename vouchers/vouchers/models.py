from datetime import datetime
from django.db import models
from django.utils.timezone import utc

network_choices = [("CellC", "CellC"), ("MTN", "MTN"), ("Vodacom", "Vodacom")]
class VoucherException(Exception):
    pass

class VoucherManager(models.Manager):

    def unallocated(self, network):
        return self.filter(network=network, allocated=False)

    def allocated_to_survey(self, survey):
        vouchers = self.filter(_surveyallocation=survey)
        if vouchers.count() == 0:
            return None
        if vouchers.count() > 1:
            raise VoucherException("Did not expect more than one Voucher allocated to the same survey allocation")
        return vouchers[0]

class Voucher(models.Model):
    voucher_number1 = models.CharField(max_length=60, null=True, blank=True)
    voucher_number2 = models.CharField(max_length=60, null=True, blank=True)
    network = models.CharField(choices=network_choices, max_length=20)
    allocated = models.BooleanField(default=False)
    allocation_date = models.DateTimeField(null=True, blank=True)

    objects = VoucherManager()

    def allocate(self, survey):
        now = datetime.utcnow().replace(tzinfo=utc)
        if self.allocated == True:
            raise VoucherException("Voucher already allocated")

        if survey.voucher != None and survey.voucher != self:
            raise VoucherException("Survey already allocated")
        survey.voucher = self
        survey.save()

        self.allocated = True
        self.allocation_date = now
        self.save()

    @property
    def surveyallocation(self):
        # Yucky stuff but by default django throws an exception on the reverse reference to a OneToOneField
        try:
           return self._surveyallocation
        except SurveyAllocation.DoesNotExist:
            return None 

    def __unicode__(self):
        return self.voucher_number

class SurveyAllocation(models.Model):
    survey_id = models.CharField(max_length=60, blank=True, null=True)
    voucher = models.OneToOneField(Voucher, null=True, related_name="_surveyallocation", blank=True)

    @property
    def is_used(self):
        return self.voucher != None

    def allocate(self, network):
        vouchers = Voucher.objects.filter(network=network, allocated=False)
        if vouchers.count() == 0:
            raise VoucherException("No vouchers available")
        else:
            voucher = vouchers[0]
            self.voucher = voucher
            self.voucher.allocate(self)
        

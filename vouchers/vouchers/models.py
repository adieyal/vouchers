from datetime import datetime
from django.db import models
from django.utils.timezone import utc

network_choices = [("CellC", "CellC"), ("MTN", "MTN")]
class VoucherException(Exception):
    pass

class VoucherManager(models.Manager):

    def unallocated(self, network):
        return self.filter(network=network, allocated=False)

    def allocated_to_survey(self, survey_id):
        if self.filter(survey_id=survey_id).count() == 0:
            return False
        return True

class Voucher(models.Model):
    voucher_number = models.CharField(max_length=60, null=True, blank=True)
    network = models.CharField(choices=network_choices, max_length=20)
    allocated = models.BooleanField(default=False)
    survey_id = models.CharField(max_length=60, blank=True, null=True)
    allocation_date = models.DateTimeField(null=True, blank=True)

    objects = VoucherManager()

    def allocate(self, survey_id):
        now = datetime.utcnow().replace(tzinfo=utc)
        if self.survey_id:
            raise VoucherException("Voucher has already been allocated")

        self.survey_id = survey_id
        self.allocated = True
        self.allocation_date = now
        self.save()

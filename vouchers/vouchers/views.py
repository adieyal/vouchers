from django.http import HttpResponse, Http404
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.views.generic.base import View
from django.shortcuts import redirect
import models
from django import forms

class DetailsForm(forms.Form):
    survey_id = forms.CharField(max_length=60)
    network = forms.ChoiceField(choices=models.network_choices)

class EnterDetails(View):
    def get(self, request): 
        return TemplateResponse(request, 'vouchers/enter_details.html', {"form" : DetailsForm()})

    def post(self, request):
        f = DetailsForm(request.POST)
        return redirect(
            "%s?survey_id=%s&network=%s" % (
                reverse("allocation"), f.data["survey_id"], f.data["network"]
            )
        )

class VoucherAllocation(View):
    def get(self, request):
        survey_id = request.GET.get("survey_id", None)

        network = request.GET.get("network", None)
        if survey_id == None or network == None:
            raise Http404

        try:
            survey = models.SurveyAllocation.objects.get(survey_id=survey_id)
            if models.Voucher.objects.allocated_to_survey(survey):
                return TemplateResponse(request, 'vouchers/already_allocated.html', {})
        except models.SurveyAllocation.DoesNotExist:
            raise Http404

        unallocated = models.Voucher.objects.unallocated(network=network)

        if unallocated.count() > 0:
            voucher = unallocated[0]
            voucher.allocate(survey)

            return TemplateResponse(request, 'vouchers/success.html', {
                voucher : voucher
            })
        else:
            return TemplateResponse(request, 'vouchers/no_voucher.html', {})

from django.test import TestCase
import models
from django.test.client import Client
from django.core.urlresolvers import reverse

allocation_url = reverse("allocation")

def unallocated_voucher(network="MTN", voucher_number1="12345", voucher_number2="67890"):
    return models.Voucher.objects.create(
        network=network,
        voucher_number1=voucher_number1,
        voucher_number2=voucher_number2,
    )

def allocated_voucher(network="MTN", voucher_number1="12345", survey=None):
    survey = survey or models.SurveyAllocation(survey_id="qwerty")
    voucher = unallocated_voucher(network, voucher_number1)
    voucher.allocate(survey)
    return voucher

class SurveyTestCase(TestCase):
    def setUp(self):
        self.survey_allocation = models.SurveyAllocation.objects.create(
            survey_id="1234"
        ) 

        self.unallocated_voucher = unallocated_voucher(network="MTN")
            

    def test_is_used(self):
        self.assertFalse(self.survey_allocation.is_used)

    def test_allocation(self):
        self.assertEquals(self.unallocated_voucher.surveyallocation, None)
        self.survey_allocation.allocate(network="MTN")
        self.unallocated_voucher = models.Voucher.objects.all()[0]
        self.assertEquals(self.unallocated_voucher.surveyallocation, self.survey_allocation)

        self.assertTrue(self.survey_allocation.is_used)
        self.assertTrue(self.unallocated_voucher.allocated)
        self.assertTrue(self.unallocated_voucher.allocation_date != None)

    def test_different_network_no_vouchers(self):
        self.assertRaises(
            models.VoucherException, self.survey_allocation.allocate, network="Vodacom"
        )

    def test_same_network_no_vouchers(self):
        self.survey_allocation.allocate(network="MTN")
        self.assertRaises(
            models.VoucherException, self.survey_allocation.allocate, network="MTN"
        )

class VoucherTestCase(TestCase):
    def setUp(self):
        self.unallocated = unallocated_voucher(network="CellC", voucher_number1="1111111111")
        self.unallocated_mtn = unallocated_voucher(network="MTN", voucher_number1="2222222222")

        self.allocated = allocated_voucher(network="CellC", voucher_number1="1234")
        self.survey1 = models.SurveyAllocation(survey_id="sdfdsfsd1")
        self.survey2 = models.SurveyAllocation(survey_id="sdfdsfsd1")

    def test_default_unallocated(self):
        self.assertFalse(self.unallocated.allocated)

    def test_network_specific_allocation(self):
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 1)
        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 1)

        self.unallocated.allocate(self.survey1)
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 0)
        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 1)

        self.unallocated_mtn.allocate(self.survey2)
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 0)
        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 0)

    def test_cannot_allocate_allocated_survey(self):

        self.unallocated.allocate(self.survey1)
        self.assertRaises(models.VoucherException, self.unallocated_mtn.allocate, self.survey1)

    def test_unallocated(self):
        unallocated = models.Voucher.objects.unallocated("CellC")
        self.assertEqual(unallocated.count(), 1)
        self.assertEqual(unallocated[0], self.unallocated)

        unallocated = models.Voucher.objects.unallocated("MTN")
        self.assertEqual(unallocated.count(), 1)

        unallocated = models.Voucher.objects.unallocated("Not a network")
        self.assertEqual(unallocated.count(), 0)

    def test_allocate(self):

        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 1)
        self.assertFalse(self.unallocated.allocated)
        self.unallocated.allocate(self.survey1)
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 0)
        self.assertTrue(self.unallocated.allocated)

    def test_already_allocated(self):

        self.assertEquals(models.Voucher.objects.allocated_to_survey(self.survey1), None)
        self.unallocated.allocate(self.survey1)
        self.assertEquals(models.Voucher.objects.allocated_to_survey(self.survey1), self.unallocated)

    def test_date_allocation(self):
        self.assertIsNone(self.unallocated.allocation_date)
        self.unallocated.allocate(self.survey1)
        self.assertIsNotNone(self.unallocated.allocation_date)

    def test_allocate_survey_from_voucher(self):
        self.unallocated.allocate(self.survey1)
        self.assertEquals(self.unallocated.surveyallocation, self.survey1)
        self.assertEquals(self.survey1.voucher, self.unallocated)

    def test_double_allocation_with_different_survey(self):
        self.unallocated.allocate(self.survey1)
        self.assertRaises(models.VoucherException, self.unallocated.allocate, self.survey2)

class EnterDetailsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_check_get_request(self):
        c = self.client

        response = c.get('/', {})
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, "vouchers/enter_details.html")
        
    
class VoucherAllocationTestCase(TestCase):
    def setUp(self):
        self.unallocated_cellc1 = unallocated_voucher(network="CellC", voucher_number1="11111111")
        self.unallocated_cellc2 = unallocated_voucher(network="CellC", voucher_number1="22222222")

        
        self.unallocated_mtn1 = unallocated_voucher(network="MTN", voucher_number1="3333333")
        self.unallocated_mtn2 = unallocated_voucher(network="MTN", voucher_number1="4444444")
        
        self.client = Client()

    def test_cannot_allocate_without_survey(self):
        c = self.client

        response = c.get(allocation_url, {})
        self.assertEquals(response.status_code, 404)

        self.survey = models.SurveyAllocation(survey_id="1234")

    def test_cannot_allocate_without_network(self):
        c = self.client

        response = c.get(allocation_url, {"survey_id" : "1234"})
        self.assertEquals(response.status_code, 404)

    def test_cannot_allocate_with_network_without_survey(self):
        c = self.client

        response = c.get(allocation_url, {"survey_id" : "1234"})
        self.assertEquals(response.status_code, 404)

    def test_with_invalid_survey(self):
        c = self.client

        response = c.get(allocation_url, {"survey_id" : "5678", "network" : "MTN"})
        self.assertEquals(response.status_code, 404)

    def test_allocate_allocated(self):

        c = self.client

        self.assertEquals(models.Voucher.objects.all().count(), 4)

        # Test that allocation allocates a voucher 
        survey_allocation = models.SurveyAllocation.objects.create(
            survey_id="1234"
        ) 

        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 2)
        response = c.get(allocation_url, {"survey_id" : survey_allocation.survey_id, "network" : "CellC"})
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 1)

        # Test with another network
        survey_allocation = models.SurveyAllocation.objects.create(
            survey_id="another voucher"
        ) 

        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 2)
        response = c.get(allocation_url, {"survey_id" : survey_allocation.survey_id, "network" : "MTN"})
        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 1)

        self.assertTemplateUsed(response, "vouchers/success.html")

    def test_success_template(self):
        survey_allocation = models.SurveyAllocation.objects.create(
            survey_id="another voucher"
        ) 

        c = self.client
        response = c.get(allocation_url, {"survey_id" : survey_allocation.survey_id, "network" : "MTN"})
        self.assertTemplateUsed(response, "vouchers/success.html")

    def test_no_available_template(self):
        survey_allocation = models.SurveyAllocation.objects.create(
            survey_id="another voucher"
        ) 

        c = self.client
        response = c.get(allocation_url, {"survey_id" : survey_allocation.survey_id, "network" : "Vodacom"})
        self.assertTemplateUsed(response, "vouchers/no_voucher.html")

    def test_already_allocated_voucher(self):
        survey_allocation = models.SurveyAllocation.objects.create(
            survey_id="another voucher"
        ) 

        c = self.client
        response = c.get(allocation_url, {"survey_id" : survey_allocation.survey_id, "network" : "MTN"})
        response = c.get(allocation_url, {"survey_id" : survey_allocation.survey_id, "network" : "MTN"})
        self.assertTemplateUsed(response, "vouchers/already_allocated.html")

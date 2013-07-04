from django.test import TestCase
import models
from django.test.client import Client
from django.core.urlresolvers import reverse

allocation_url = reverse("allocation")

class VoucherTestCase(TestCase):
    def setUp(self):
        self.unallocated = models.Voucher.objects.create(
            network="CellC",  
            voucher_number="11111111111"
        )

        self.unallocated_mtn = models.Voucher.objects.create(
            network="MTN",  
            voucher_number="2222222222"
        )

        self.allocated = models.Voucher.objects.create(
            voucher_number="1234",
            survey_id="blahblah",
            network="CellC",
            allocated=True
        )

    def test_default_unallocated(self):
        self.assertFalse(self.unallocated.allocated)

    def test_network_specific_allocation(self):
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 1)
        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 1)
        self.unallocated.allocate("cellc voucher")
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 0)
        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 1)

        self.unallocated_mtn.allocate("mtn voucher")
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 0)
        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 0)

    def test_double_allocation_error(self):
        self.unallocated.allocate("cellc voucher")
        self.assertRaises(models.VoucherException, self.unallocated.allocate, "another voucher")

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
        self.unallocated.allocate("My survey id")
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 0)
        self.assertTrue(self.unallocated.allocated)

    def test_already_allocated(self):
        self.assertFalse(models.Voucher.objects.allocated_to_survey("my_voucher"))
        self.unallocated.allocate("my_voucher")
        self.assertTrue(models.Voucher.objects.allocated_to_survey("my_voucher"))
            

    def test_date_allocation(self):
        self.assertIsNone(self.unallocated.allocation_date)
        self.unallocated.allocate("my_voucher")
        self.assertIsNotNone(self.unallocated.allocation_date)

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
        self.unallocated_cellc = models.Voucher.objects.create(
            network="CellC",
            voucher_number="333333333333"
        )

        self.unallocated_cellc2 = models.Voucher.objects.create(
            network="CellC",
            voucher_number="444444444444"
        )

        self.unallocated_mtn = models.Voucher.objects.create(
            network="MTN",
            voucher_number="55555555555"
        )

        self.unallocated_mtn2 = models.Voucher.objects.create(
            network="MTN",
            voucher_number="66666666666666"
        )
        
        self.client = Client()

    def test_allocate_allocated(self):
        c = self.client

        response = c.get(allocation_url, {})
        self.assertEquals(response.status_code, 404)

        response = c.get(allocation_url, {"survey_id" : "3434"})
        self.assertEquals(response.status_code, 404)

        response = c.get(allocation_url, {"network" : "3434"})
        self.assertEquals(response.status_code, 404)

        self.assertEquals(models.Voucher.objects.all().count(), 4)

        # Two vouchers are allocated at the same time
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 2)
        response = c.get(allocation_url, {"survey_id" : "allocated id", "network" : "CellC"})
        self.assertEquals(models.Voucher.objects.unallocated("CellC").count(), 0)

        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 2)
        response = c.get(allocation_url, {"survey_id" : "another voucher", "network" : "MTN"})
        self.assertEquals(models.Voucher.objects.unallocated("MTN").count(), 0)

        self.assertTemplateUsed(response, "vouchers/success.html")

    def test_cannot_allocate_with_only_one_voucher(self):
        c = self.client
        self.unallocated_mtn.allocate("some voucher")
        response = c.get(allocation_url, {"survey_id" : "another id", "network" : "MTN"})
        self.assertTemplateUsed(response, "vouchers/no_voucher.html")

    def test_success_template(self):
        c = self.client
        response = c.get(allocation_url, {"survey_id" : "allocated id", "network" : "MTN"})
        self.assertTemplateUsed(response, "vouchers/success.html")

    def test_no_available_template(self):
        c = self.client
        response = c.get(allocation_url, {"survey_id" : "allocated id", "network" : "MTN"})
        response = c.get(allocation_url, {"survey_id" : "another id", "network" : "MTN"})
        self.assertTemplateUsed(response, "vouchers/no_voucher.html")

    def test_already_allocated_voucher(self):
        c = self.client
        response = c.get(allocation_url, {"survey_id" : "allocated id", "network" : "MTN"})
        response = c.get(allocation_url, {"survey_id" : "allocated id", "network" : "MTN"})
        self.assertTemplateUsed(response, "vouchers/already_allocated.html")

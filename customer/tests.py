"""Offline smoke tests: run with
DJANGO_SETTINGS_MODULE=img_reg_lowes.settings_ci python manage.py test
(no camera, no dlib build, no network; FCM is never called here)."""
from django.test import TestCase
from rest_framework.test import APIClient

from .models import Offers, SalesRepresentative


class SmokeTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_login_logout(self):
        payload = {"email": "rep@example.com", "password": "pw-123456",
                   "device_token": "tok", "device_type": "android",
                   "first_name": "A", "middle_name": "", "last_name": "B"}
        r = self.client.post("/api/sales-rep-register", payload, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        self.assertTrue(SalesRepresentative.objects.filter(email="rep@example.com").exists())

        r = self.client.post("/api/sales-rep-login", payload, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        bad = dict(payload, password="wrong")
        r = self.client.post("/api/sales-rep-login", bad, format="json")
        self.assertEqual(r.status_code, 400)

        rep_id = SalesRepresentative.objects.get(email="rep@example.com").id
        r = self.client.post("/api/logout", {"sales_rep_id": rep_id}, format="json")
        self.assertEqual(r.status_code, 200)

    def test_list_offers(self):
        Offers.objects.create(category="paint", description="10% off", image="offers/x.png")
        r = self.client.post("/api/list-offers", {"category": "paint"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("10% off", r.content.decode())

    def test_sales_rep_details_404_or_ok(self):
        r = self.client.get("/api/cust-order-details/999")
        self.assertIn(r.status_code, (200, 404))

    def test_admin_login_page(self):
        self.assertEqual(self.client.get("/admin/login/").status_code, 200)

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

        r_ok = self.client.post("/api/sales-rep-login", payload, format="json")
        self.assertEqual(r_ok.status_code, 200, r_ok.content)
        bad = dict(payload, password="wrong")
        r = self.client.post("/api/sales-rep-login", bad, format="json")
        self.assertEqual(r.status_code, 400)

        token = r_ok.json()["data"][0]["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        r = self.client.post("/api/logout", {}, format="json")
        self.assertEqual(r.status_code, 200)

    def test_list_offers(self):
        Offers.objects.create(category="paint", description="10% off", image="offers/x.png")
        r = self.client.post("/api/list-offers", {"category": "paint"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("10% off", r.content.decode())

    def test_sales_rep_details_404_or_ok(self):
        r = self.client.get("/api/cust-order-details/999")
        self.assertIn(r.status_code, (401, 403))  # now requires a sales-rep token

    def test_admin_login_page(self):
        self.assertEqual(self.client.get("/admin/login/").status_code, 200)


class SecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.rep = SalesRepresentative.objects.create_sales_rep_email(
            email="sec@example.com", password="pw-123456",
            extra_fields={"first_name": "S", "middle_name": "", "last_name": "R"})
        self.other = SalesRepresentative.objects.create_sales_rep_email(
            email="other@example.com", password="pw-654321",
            extra_fields={"first_name": "O", "middle_name": "", "last_name": "R"})

    def _login(self, email="sec@example.com", password="pw-123456"):
        r = self.client.post("/api/sales-rep-login",
                             {"email": email, "password": password,
                              "device_token": "t", "device_type": "android"}, format="json")
        self.assertEqual(r.status_code, 200, r.content)
        return r.json()["data"][0]["token"]

    def test_protected_endpoints_require_token(self):
        for url in (f"/api/sales-rep-details/{self.rep.id}",
                    "/api/cust-order-details/1",
                    "/api/cust_details_purchase_history/1"):
            self.assertIn(self.client.get(url).status_code, (401, 403), url)
        self.assertIn(self.client.post("/api/logout", {"sales_rep_id": self.rep.id},
                                       format="json").status_code, (401, 403))

    def test_forged_token_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token not-a-real-token")
        self.assertEqual(self.client.get(f"/api/sales-rep-details/{self.rep.id}").status_code, 401)

    def test_token_access_and_ownership(self):
        token = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        self.assertEqual(self.client.get(f"/api/sales-rep-details/{self.rep.id}").status_code, 200)
        self.assertEqual(self.client.get(f"/api/sales-rep-details/{self.other.id}").status_code, 403)

    def test_logout_uses_token_identity_and_revokes(self):
        token = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        # A body id for someone else is ignored; only the caller is logged out.
        r = self.client.post("/api/logout", {"sales_rep_id": self.other.id}, format="json")
        self.assertEqual(r.status_code, 200)
        self.other.refresh_from_db(); self.rep.refresh_from_db()
        self.assertEqual(self.other.status, "available")
        self.assertEqual(self.rep.status, "not_available")
        self.assertEqual(self.client.get(f"/api/sales-rep-details/{self.rep.id}").status_code, 401)

    def test_unknown_email_login_is_400_not_500(self):
        r = self.client.post("/api/sales-rep-login",
                             {"email": "nobody@example.com", "password": "x",
                              "device_token": "t", "device_type": "android"}, format="json")
        self.assertEqual(r.status_code, 400)

    def test_settings_hardening(self):
        from django.conf import settings
        self.assertFalse(settings.DEBUG)
        self.assertNotIn("*", settings.ALLOWED_HOSTS)

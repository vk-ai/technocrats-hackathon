"""Minimal signed-token auth for the sales-rep API.

SalesRepresentative is not a Django auth user, so instead of DRF's TokenAuthentication
(which needs auth.User) the login view issues a token signed with SECRET_KEY
(django.core.signing, salted, time-limited). Clients send
``Authorization: Token <token>``.
"""
from django.conf import settings
from django.core import signing
from rest_framework import authentication, exceptions, permissions

from .models import SalesRepresentative

_SALT = "customer.sales-rep-token"


def issue_token(rep):
    return signing.dumps({"rep": rep.id}, salt=_SALT)


class SalesRepTokenAuthentication(authentication.BaseAuthentication):
    keyword = "Token"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).split()
        if not header or header[0].lower() != self.keyword.lower().encode():
            return None
        if len(header) != 2:
            raise exceptions.AuthenticationFailed("Invalid token header.")
        try:
            data = signing.loads(header[1].decode(), salt=_SALT,
                                 max_age=settings.SALES_REP_TOKEN_MAX_AGE)
        except (signing.BadSignature, UnicodeDecodeError):
            raise exceptions.AuthenticationFailed("Invalid or expired token.")
        try:
            rep = SalesRepresentative.objects.get(id=data["rep"])
        except SalesRepresentative.DoesNotExist:
            raise exceptions.AuthenticationFailed("Invalid token.")
        if rep.status == "not_available":
            # Logged out: tokens issued before logout are no longer accepted.
            raise exceptions.AuthenticationFailed("Session ended. Please log in again.")
        return rep, header[1].decode()

    def authenticate_header(self, request):
        return self.keyword


class IsSalesRep(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user, SalesRepresentative)

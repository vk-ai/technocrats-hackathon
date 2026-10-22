"""CI/offline settings: stub the heavy CV deps (dlib/face_recognition, OpenCV)
so Django checks, migrations and smoke tests run without a camera or dlib build."""
import sys
import types

for _name in ("cv2", "face_recognition"):
    try:
        __import__(_name)
    except Exception:  # pragma: no cover - only when the dep is absent
        sys.modules[_name] = types.ModuleType(_name)

import os  # noqa: E402

# CI-only, non-secret values so settings.py does not refuse to start.
os.environ.setdefault("DJANGO_SECRET_KEY", "ci-only-not-a-secret")
os.environ.setdefault("DJANGO_ALLOWED_HOSTS", "testserver,localhost")

from .settings import *  # noqa: E402,F401,F403

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}

"""
WSGI config for yaqdha_platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yaqdha_platform.settings')

application = get_wsgi_application()

import django
from django.contrib.auth.models import User

try:
    django.setup()
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'ubas2004')
        print("Done: Admin created!")
except Exception as e:
    print(f"Error: {e}")


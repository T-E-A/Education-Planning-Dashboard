"""
ASGI config for DataLayer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see:
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# point Django to the right settings module and set up the ASGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Server_Configuration_and_Settings.settings')

application = get_asgi_application()

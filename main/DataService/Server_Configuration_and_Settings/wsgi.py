"""
WSGI config for DataLayer project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# point Django to the right settings module and set up the WSGI application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Server_Configuration_and_Settings.settings')

application = get_wsgi_application()

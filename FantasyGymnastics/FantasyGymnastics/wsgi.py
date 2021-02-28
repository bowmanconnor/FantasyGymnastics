"""
WSGI config for FantasyGymnastics project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
import socket

from django.core.wsgi import get_wsgi_application

if 'django' in socket.gethostname():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FantasyGymnastics.settings.development')

application = get_wsgi_application()

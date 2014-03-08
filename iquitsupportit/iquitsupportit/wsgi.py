"""
WSGI config for iquitsupportit project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
import sys
ppath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
print ppath
sys.path.append(ppath)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

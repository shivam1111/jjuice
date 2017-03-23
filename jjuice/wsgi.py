"""
WSGI config for jjuice project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

from django.core.wsgi import get_wsgi_application
import os,sys

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.insert(0, os.path.join(root_path, 'ocentag_project'))
sys.path.insert(0, root_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jjuice.settings")

application = get_wsgi_application()

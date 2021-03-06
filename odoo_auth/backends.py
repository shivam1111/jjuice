from django.contrib.auth import get_user_model
from odoo_auth.models import OdooUser
from odoo_helpers import authenticate
from django.conf import settings
import xmlrpclib
import logging
logger = logging.getLogger(__name__)
User = get_user_model()

class OdooBackend(object):

    ODOO_SERVER_URL = None
    ODOO_SERVER_PORT = None
    ODOO_SERVER_DBNAME = None
    ODOO_SOCK_COMMON = None

    def __init__(self):
        self.ODOO_SERVER_URL = settings.ODOO_URL
        self.ODOO_SERVER_PORT = settings.ODOO_SERVER_PORT
        self.ODOO_SERVER_DBNAME = settings.ODOO_DB

        if not self.ODOO_SERVER_PORT:
            #If ODOO_SERVER_PORT == 0 or False, you use port standard 80
            url_login = ''.join([self.ODOO_SERVER_URL, '/xmlrpc/common'])
        else:
            url_login = ''.join([self.ODOO_SERVER_URL, '/xmlrpc/common'])
        self.ODOO_SOCK_COMMON = xmlrpclib.ServerProxy(url_login)

    def authenticate(self, username=None, password=None):
        user = None
        try:
            odoo_id = self.ODOO_SOCK_COMMON.login(self.ODOO_SERVER_DBNAME, username, password)
            if odoo_id:
                try:
                    user = User.objects.get(odoo_id=odoo_id)
                except User.DoesNotExist:
                    user, created = User.objects.get_or_create(username=username,odoo_id=odoo_id)
                    user.save()
        except Exception, e:
            logger.error('Exception with Odoo authentificate : %s' % e)
            return None
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logger.error('No Odoo user identified with id : %s' % user_id)
            return None
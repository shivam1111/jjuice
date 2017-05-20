from rpc4django import rpcmethod
from django.conf import settings
from django.contrib.auth import get_user_model
# The doc string supports reST if docutils is installed
@rpcmethod(name='odoo.delete_user', signature=['boolean', 'int'],login_required=True)
def delete_user(user_id):
    try:
        User = get_user_model()
        user = User.objects.get(odoo_id = user_id)
        user.delete()
        return True
    except User.DoesNotExist:
        return True
    except Exception as e:
        return False


# from xmlrpclib import ServerProxy
# s = ServerProxy('http://admin:shivam@127.0.0.1:8000')
# s.rpc4django.delete_user()
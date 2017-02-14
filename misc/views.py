from django.shortcuts import render
# from odoo.models import Newsletter
import urlparse
from django.http import HttpResponseRedirect
from models import NewsletterContact,MailingList
from odoo.models import IrConfigParameters
from odoo_helpers import get_login_authenticate

def newsletter(request):
    name = ''
    newletter_list_id  = IrConfigParameters.objects.get_param('mailing_list_id')
    
    if newletter_list_id:
        newsletter_list = MailingList.objects.get(id=eval(newletter_list_id))
        if request.GET and request.GET.get('email',False):
            if request.user.is_authenticated():
                name = request.user.first_name
            dummy,odoo_uid = get_login_authenticate()
            NewsletterContact(name=name,email=request.GET.get('email',''),
                              list_id=newsletter_list,
                              write_uid = odoo_uid,
                              create_uid = odoo_uid,
                              ).save()
    return HttpResponseRedirect('/')
        
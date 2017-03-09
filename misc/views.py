from django.shortcuts import render
# from odoo.models import Newsletter
import urlparse,os
from django.http import HttpResponseRedirect,HttpResponse
from models import NewsletterContact,MailingList,HrEmployee
from odoo.models import IrConfigParameters
from catalog.models import S3Object
from odoo_helpers import get_login_authenticate
from django.views import View
from django.conf import settings
from helper import create_aws_url
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

class AboutUs(View):
    
    def get(self,request,template_name="aboutus.html"):
        banner_url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_BANNER_IMAGE)
        banner_record =  S3Object.objects.filter(aboutus_banner=True)[:1]
        name = "About Us"
        if banner_record.exists():
            banner_url = create_aws_url(banner_record[0]._meta.db_table,str(banner_record[0].id)) 
        employees = HrEmployee.objects.filter(publish=True).order_by('sequence')
        return render(request,template_name,locals())

class ContactUs(View):
    
    def get(self,request,template_name="contactus.html"):
        banner_url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_BANNER_IMAGE)
        banner_record =  S3Object.objects.filter(contactus_banner=True)[:1]
        name = "Contact Us"
        if banner_record.exists():
            banner_url = create_aws_url(banner_record[0]._meta.db_table,str(banner_record[0].id))         
        return render(request,template_name,locals())    

    def post(self,request,template_name="contactus.html"):
        url =  reverse('misc:contactus',args=[])
        subject, from_email, to = 'Contact Request from Website', request.POST.get('email','hello@vapejjuice.com'), settings.CONTACTUS_EMAIL
        html_content = render_to_string('contactus_email.html', {
                                        'name':request.POST.get('name','No Name'),
                                        'email':request.POST.get('email','No Email'),
                                        'website':request.POST.get('website','-'),
                                        'message':request.POST.get('message','-'),
                                        })
        text_content = strip_tags(html_content) # this strips the html, so people will have the text as well.
        # create the email, and attach the HTML version as well.
        msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        return HttpResponseRedirect(url)

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

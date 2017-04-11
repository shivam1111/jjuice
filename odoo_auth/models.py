from django.db import models
from odoo.models import ResUsers
from django.contrib.auth.models import AbstractUser
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.template import Context
import urllib,uuid,datetime
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

class OdooUser(AbstractUser):
    REQUIRED_FIELDS = ['odoo_id','email']

    odoo_id = models.BigIntegerField(blank=False,null=False,verbose_name = "Odoo ID",unique=True)
    token_password = models.UUIDField("Token",blank=True,null=True)
    token_expiration = models.DateTimeField('Token Expiration',blank=True,null=True)
        
    def send_reset_password_mail(self,request):
        # Send an HTML email with an embedded image and a plain text message for
        # email clients that don't want to display the HTML.
        self.token_password =  uuid.uuid4()
        self.token_expiration = datetime.datetime.now() + datetime.timedelta(hours=1)
        self.save();
        query = urllib.urlencode({'token':self.token_password})
        reset_link = request.build_absolute_uri()
        reset_link = "?".join([reset_link,query])
        ctx = {
                'reset_link':reset_link,
                'current_site':get_current_site(request).domain
            }
        message = get_template('forgot_password.html').render(Context(ctx))
        subject, from_email, to = 'Reset Password', settings.EMAIL_HOST_USER, [self.odoo_user.login]
        # Create the root message and fill in the from, to, and subject headers
        msg = EmailMessage(subject, message, to=to, from_email=from_email)
        msg.content_subtype = 'html'
        msg.send()
    
    
    @property
    def odoo_user(self):
        try:
            return ResUsers.objects.get(id=self.odoo_id)
        except ResUsers.DoesNotExist:
            return None
        
        
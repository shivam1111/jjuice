from __future__ import unicode_literals

from django.db import models

class MailingList(models.Model):
    id = models.IntegerField(primary_key=True)
    name = name = models.CharField(verbose_name = "Name",blank=False,max_length = 100)
    
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "mail_mass_mailing_list"
        
class NewsletterContact(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name="Email")
    name = models.CharField(verbose_name="Name",max_length=100,blank=True)
    list_id = models.ForeignKey(MailingList,verbose_name = "Mailing List",
                                db_column='list_id',blank=False,related_name="subscriber_ids")
    create_date = models.DateTimeField(auto_now_add=True)
    write_date = models.DateTimeField(auto_now=True)
    write_uid = models.IntegerField('Write UID')
    create_uid = models.IntegerField('Write UID')
    opt_out= models.NullBooleanField('Opt Out')
    
    
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "mail_mass_mailing_contact"    
    
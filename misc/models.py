from __future__ import unicode_literals
from django.db import models
from catalog.models import ProductFlavors
from odoo.models import Partner

_RATING = [
        ('1','Very Bad'),
        ('2','Bad'),
        ('3', 'Normal'),
        ('4', 'Good'),
        ('5','Very Good')
    ] 
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

class HrJob(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name="Name",max_length=100,blank=True)
    state = models.CharField(verbose_name='State',max_length=50,
                             choices=[('open','Recruitment Closed'),('recruit','Recruitment Open')])
    
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "hr_job"                

class HrEmployee(models.Model):
    id = models.AutoField(primary_key=True)
    sequence = models.IntegerField('Sequence')
    work_email = models.EmailField(verbose_name="Work Email")
    name_related = models.CharField(verbose_name="Name",max_length=100,blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    write_date = models.DateTimeField(auto_now=True)
    write_uid = models.IntegerField('Write UID')
    create_uid = models.IntegerField('Write UID')
    publish = models.NullBooleanField('Publish on Website')
    image_medium = models.BinaryField("Image")
    image = models.BinaryField("Image")
    job_id = models.ForeignKey(HrJob,db_column="job_id",verbose_name = "Job Title",related_name ="employee_ids",blank=True)
    
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "hr_employee"  
        
class PartnerReviews(models.Model):

    id = models.AutoField(primary_key=True)
    sequence = models.IntegerField('Sequence')
    partner_id = models.ForeignKey(Partner,
                                   db_column = "partner_id",
                                   verbose_name = "Partner",
                                   related_name = "partner_review_ids",blank=True) 
    review = models.TextField(verbose_name = "Review")
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "partner_reviews"         
    
              
    
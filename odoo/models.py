from __future__ import unicode_literals
from django.db import models
from docutils.nodes import description

class S3Object(models.Model):
    id = models.IntegerField(primary_key=True)
    file_name = models.CharField(verbose_name = "Name",blank=False,max_length = 200)
    store_fname = models.CharField(verbose_name = "Name",blank=False,max_length = 200)
    url = models.URLField(verbose_name = "File URL")
    folder_key = models.CharField(verbose_name = "Name",blank=False,max_length = 100)

    _DATABASE = "odoo"    
    class Meta:
        managed=False
        db_table = "s3_object"   
            
class WebsiteBanner(models.Model):
    id = models.IntegerField(primary_key=True)
    s3_object_id = models.ForeignKey(S3Object,verbose_name='S3Object',blank=False,db_column="s3_object_id",related_name="banner_s3_object_ids")
    sequence = models.IntegerField(verbose_name = "Sequence")
    
    _DATABASE = "odoo"    
    class Meta:
        managed=False
        db_table = "website_banner"
        
class WebsitePolicy(models.Model):
    id = models.IntegerField(primary_key=True)
    s3_object_id = models.ForeignKey(S3Object,verbose_name='S3Object',blank=False,db_column="s3_object_id",related_name="policy_s3_object_ids")
    sequence = models.IntegerField(verbose_name = "Sequence")
    description = models.TextField(verbose_name = "Description",blank=True)
    name = models.CharField(verbose_name = "Name", max_length=100)

    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "website_policy"           

class IrConfigParametersManager(models.Manager):
    def get_param(self,param):
        try:
            return self.get_queryset().get(key=param).value
        except self.model.DoesNotExist:
            return False
    
class IrConfigParameters(models.Model):
    id = models.IntegerField(primary_key=True)
    key = models.CharField(verbose_name = "key", max_length=100)
    value = models.TextField(verbose_name = "Value")
    objects = IrConfigParametersManager()
    
    
    _DATABASE = "odoo"    
    class Meta:
        managed=False
        db_table = "ir_config_parameter"               
    
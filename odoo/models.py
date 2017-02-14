from __future__ import unicode_literals
from django.db import models
from docutils.nodes import description
from helper import create_aws_url

_PRODUCT_TYPES = [
        ('product','Stockable Product'),
        ('consu','Consumable Product'),
        ('service','Service'),
    ]


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
    sequence = models.IntegerField(verbose_name = "Sequence")
    file_name = models.CharField(verbose_name = "File Name", max_length=100)
    
    def get_image_url(self):
        return create_aws_url(self._meta.db_table,str(self.id))
        
    
    _DATABASE = "odoo"    
    class Meta:
        managed=False
        db_table = "website_banner"
        
class WebsitePolicy(models.Model):
    id = models.IntegerField(primary_key=True)
    sequence = models.IntegerField(verbose_name = "Sequence")
    description = models.TextField(verbose_name = "Description",blank=True)
    name = models.CharField(verbose_name = "Name", max_length=100)

    def get_image_url(self):
        return create_aws_url(self._meta.db_table,str(self.id))

    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "website_policy"           

class IrConfigParametersManager(models.Manager):
    def get_param(self,param,default=False):
        try:
            return self.get_queryset().get(key=param).value
        except self.model.DoesNotExist:
            return default
    
class IrConfigParameters(models.Model):
    id = models.IntegerField(primary_key=True)
    key = models.CharField(verbose_name = "key", max_length=100)
    value = models.TextField(verbose_name = "Value")
    objects = IrConfigParametersManager()
    
    
    _DATABASE = "odoo"    
    class Meta:
        managed=False
        db_table = "ir_config_parameter"  

class ProductAttribute(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(verbose_name = "Name",blank=False,max_length = 50)
        
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "product_attribute"    

class ProductAttributeValue(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(verbose_name = "Name",blank=False,max_length = 50)
    attribute_id = models.ForeignKey(ProductAttribute,verbose_name = "Product Attribute Value",blank=False,
                                     db_column="attribute_id",
                                     related_name="attribute_value_ids")
    weight = models.FloatField(verbose_name="Weight",blank=True)
    ratio = models.FloatField(verbose_name='VG/PG Ratio',blank=True)
    wholesale_price = models.FloatField(verbose_name="Wholesale Price",blank=True)
    msrp = models.FloatField(verbose_name="MSRP",blank=True)
    old_price = models.FloatField(verbose_name="Wholesale Price",blank=True)
    
        
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "product_attribute_value"

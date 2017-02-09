from __future__ import unicode_literals
from django.db import models
from docutils.nodes import description

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
        
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "product_attribute_value"        

class ProductTemplate(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(verbose_name = "Stone Name",blank=False,max_length = 50)
     
    
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "product_template"

class ProductVariant(models.Model):
#     name = models.CharField(verbose_name = "Stone Name",blank=False,max_length = 50)
    id = models.IntegerField(primary_key=True)
    active = models.NullBooleanField(verbose_name="Active")
    shipping = models.NullBooleanField(verbose_name="Shipping")
    sale_ok = models.NullBooleanField(verbose_name="Can be Sold")
    type = models.CharField(max_length = 20,verbose_name = "Type",choices = _PRODUCT_TYPES)
    lst_price = models.FloatField(verbose_name="Total Price",blank=True,null=True)
    description = models.TextField(verbose_name = "Remarks")
    product_tmpl_id = models.ForeignKey(ProductTemplate,verbose_name = "Product Template",
                                        db_column = "product_tmpl_id" , 
                                        blank=False,
                                        related_name="product_variant_ids")

    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "product_product"        
             
    
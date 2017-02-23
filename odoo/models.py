from __future__ import unicode_literals
from django.db import models
from helper import create_aws_url

_PRODUCT_TYPES = [
        ('product','Stockable Product'),
        ('consu','Consumable Product'),
        ('service','Service'),
    ]
_CLASSIFICATION_FINANCE = [
        ('retailer','Retailer'),
        ('wholesale','WholeSale'),
        ('private_label','Private Label'),
        ('website','Website Visitor')
    ]

import base64

class Base64Field(models.TextField):

    def contribute_to_class(self, cls, name):
        if self.db_column is None:
            self.db_column = name
        self.field_name = name + '_base64'
        super(Base64Field, self).contribute_to_class(cls, self.field_name)
        setattr(cls, name, property(self.get_data, self.set_data))

    def get_data(self, obj):
        return getattr(obj, self.field_name)
#         return base64.decodestring(getattr(obj, self.field_name))

    def set_data(self, obj, data):
        setattr(obj, self.field_name, base64.encodestring(data))

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
    sequence = models.IntegerField(verbose_name="sequence")
    
        
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "product_attribute_value"

class Country(models.Model):
    name = models.CharField(verbose_name = "Name",blank=False,max_length = 60)
    code = models.CharField(verbose_name = "Name",blank=False,max_length = 2)
    id = models.IntegerField(primary_key=True)
    
    _DATABASE = "odoo"    
    class Meta:
        managed=False
        db_table = "res_country"

class Partner(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(verbose_name="Name",blank=False,max_length = 50)
    image = models.BinaryField(verbose_name = "Image",db_column="image")
    is_company = models.NullBooleanField("Is Company")
    parent_id = models.ForeignKey('self',verbose_name = "Company",blank=True,related_name="child_ids",db_column = "parent_id",null=True)
    city = models.CharField(verbose_name="City",blank=True,max_length = 60)
    country_id = models.ForeignKey(Country,verbose_name = "Country",db_column = "country_id",null=True)
    email = models.EmailField(verbose_name = "Email",blank=True)
    classify_finance = models.CharField(max_length=20,verbose_name="Account Classification",choices = _CLASSIFICATION_FINANCE)
    
    _DATABASE = "odoo"    
    
    class Meta:
        managed=False
        db_table = "res_partner"                

class ResUsers(models.Model):
    id = models.IntegerField(primary_key=True)
    login  = models.CharField(verbose_name="Login",max_length = 64,blank=False)
    partner_id = models.ForeignKey(Partner,db_column = "partner_id",blank=False,verbose_name = "Partner") 

    _DATABASE = "odoo"    
    
    class Meta:
        managed=False
        db_table = "res_users"
    
class VolumePricesLine(models.Model):
    id = models.IntegerField(primary_key=True)
    product_attribute = models.ForeignKey(ProductAttributeValue,db_column="product_attribute",verbose_name="Product Attribute",blank=False)
    price = models.FloatField(verbose_name="Price")
    customer_id = models.ForeignKey(Partner,db_column = "customer_id",verbose_name="Partner",blank=False,related_name = "volume_price_line_ids")
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "volume_prices_line"
        
            
                        
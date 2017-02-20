from __future__ import unicode_literals
from odoo.models import ProductAttributeValue
from django.db import models
from helper import create_aws_url
from django.conf import settings
import os
from rest_framework.compat import is_authenticated

_TAB_STYLES = [
    (1,'Flavor Concentration Matrix'),
    (2,'Product List'),
    (3,'Marketing'),
    (4,'Free Sample List'),
    (5,'Free Sample Matrix'),
]
_PRODUCT_TYPES = [
        ('product','Stockable Product'),
        ('consu','Consumable Product'),
        ('service','Service'),
    ]

_RATING = [
        ('0','Very Bad'),
        ('1','Bad'),
        ('2', 'Normal'),
        ('3', 'Good'),
        ('4','Very Good')
    ] 

class ProductFlavors(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100,verbose_name="Name",blank=False)
    create_date = models.DateTimeField(verbose_name="Created Date") 
    file_name = models.CharField(verbose_name="Created Date",max_length=100,blank=False)
    short_description = models.TextField(verbose_name = "Short Description")
    long_description = models.TextField(verbose_name = "Long Description")

    def get_price(self,request,volume):
        if  request.user.is_authenticated():
            pass
        else:
            volume.msrp

    def get_image_url(self):
        url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_IMAGE)
        if self.file_name:
            url = create_aws_url(self._meta.db_table,str(self.id)) 
        return url   
    
    _DATABASE = "odoo"    
    class Meta:
        managed=False
        db_table = "product_flavors"
        
class ProductTab(models.Model):
    id = models.IntegerField(primary_key=True)
    tab_style = models.CharField(max_length=20,verbose_name="Tab Style",choices = _TAB_STYLES)
    vol_id = models.ForeignKey(ProductAttributeValue,verbose_name = "Volume",blank=False,
                                     db_column="vol_id",
                                     related_name="tab_ids")
    consumable_stockable = models.CharField(max_length=20,verbose_name="Product Type",choices = _PRODUCT_TYPES)
    visible_all_customers = models.NullBooleanField(verbose_name="Visible to all customers")
    
    _DATABASE = "odoo"    
    class Meta:
        managed=False
        db_table = "product_tab"

class FlavorConcDetails(models.Model):
    id = models.IntegerField(primary_key=True)
    flavor_id = models.ForeignKey(ProductFlavors,verbose_name = "Flavor",blank=False,
                                     db_column="flavor_id",
                                     related_name="flavor_conc_ids")
    tab_id = models.ForeignKey(ProductTab,verbose_name = "Product Tabs",blank=False,
                                     db_column="tab_id",
                                     related_name="flavor_tab_ids")

        
    _DATABASE = "odoo"
        
    class Meta:
        managed=False
        db_table = "flavor_conc_details"

class ProductTemplate(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(verbose_name = "Stone Name",blank=False,max_length = 50)
    type = models.CharField(max_length = 20,verbose_name = "Type",choices = _PRODUCT_TYPES)
    list_price = models.FloatField(verbose_name="Total Price",blank=True,null=True)
    description = models.TextField(verbose_name = "Remarks")
    sale_ok = models.NullBooleanField(verbose_name="Can be Sold")
     
    
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "product_template"

class ProductVariant(models.Model):

    def get_image_url(self):
        url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_IMAGE)
        if self.file_name:
            url = create_aws_url(self._meta.db_table,str(self.id))
        return url 

    id = models.IntegerField(primary_key=True)
    product_tmpl_id = models.ForeignKey(
                                    ProductTemplate,verbose_name = "Product Template",
                                    db_column = "product_tmpl_id" , 
                                    blank=False,
                                    related_name="product_variant_ids"
                                )
    vol_id = models.ForeignKey(ProductAttributeValue,verbose_name="Volume",
                               db_column = "vol_id",
                               blank=False,
                               related_name="volume_product_variant_ids"
                               )
    conc_id = models.ForeignKey(ProductAttributeValue,verbose_name="Volume",
                               db_column = "conc_id",
                               blank=False,
                               related_name="conc_product_variant_ids"
                               ) 
    
    tab_id = models.ForeignKey(ProductAttributeValue,verbose_name="Volume",
                               db_column = "tab_id",
                               blank=False,
                               related_name="tab_product_variant_ids"
                               )
    flavor_id = models.ForeignKey(ProductFlavors,verbose_name="Flavor",
                                  db_column = "flavor_id",
                                  blank=False,
                                  related_name="flavor_product_variant_ids"
                              )
           
    active = models.NullBooleanField(verbose_name = "Active")
    shipping = models.NullBooleanField(verbose_name = "Shipping")
    file_name = models.CharField(verbose_name = "File Name",max_length=100)
    
    
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "product_product"

class FlavorReviews(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(verbose_name="Email")
    title = models.CharField(verbose_name="Name",max_length=200,blank=True)
    name = models.CharField(verbose_name="Name",max_length=100,blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    write_date = models.DateTimeField(auto_now=True)
    write_uid = models.IntegerField('Write UID')
    create_uid = models.IntegerField('Write UID')
    flavor_id = models.ForeignKey(ProductFlavors,verbose_name = "Flavor",db_column="flavor_id",blank=False,
                                  related_name = "flavor_review_ids"
                              )
    rating = models.CharField(max_length=20,verbose_name="Rating",choices = _RATING)
    description = models.TextField('Description')
    
    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "flavor_reviews"    
            
        
            
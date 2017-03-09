from __future__ import unicode_literals
from odoo.models import ProductAttributeValue,Partner
from django.db import models
from helper import create_aws_url
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.six.moves.urllib.parse import urlencode
import os
from pip.utils.outdated import SELFCHECK_DATE_FMT

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
    file_name = models.CharField(verbose_name="File Name",max_length=100,blank=False)
    banner_file_name = models.CharField(verbose_name="Banner Image Name",max_length=100,blank=True)
    short_description = models.TextField(verbose_name = "Short Description")
    long_description = models.TextField(verbose_name = "Long Description")
    banner_key = "product_flavor_banner"
    
    def get_url(SELFCHECK_DATE_FMT):
        return reverse('catalog:flavor',args=[self.id])
        
    def get_price(self,user,volume):
        if user and (not user.is_anonymous()):
            price_line = user.odoo_user.partner_id.volume_price_line_ids.filter(product_attribute_id=volume.id)[:1]
            if price_line.exists():
                return price_line[0].price
            elif user.odoo_user.partner_id.classify_finance in ['wholesale','private_label']:
                return volume.wholesale_price
        return volume.msrp

    def get_image_url(self,volume_id):
        image_line = self.flavor_attribute_image_ids.filter(attribute_id=volume_id)[:1]
        url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_FLAVOR_IMAGE)
        if image_line.exists():
            url = create_aws_url(image_line[0]._meta.db_table,str(image_line[0].id)) 
        return url   

    def get_banner_url(self):
        url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_BANNER_IMAGE)
        if self.banner_file_name:
            url = create_aws_url(self.banner_key,str(self.id)) 
        return url       
    
    
    _DATABASE = "odoo"    

    class Meta:
        managed=False
        db_table = "product_flavors"

class S3Object(models.Model):
    id = models.IntegerField(primary_key=True)
    file_name = models.CharField(verbose_name = "Name",blank=False,max_length = 200)
    sequence = models.IntegerField('Sequence')
    attribute_id = models.ForeignKey(ProductAttributeValue,verbose_name="Attribute",
                                  db_column="attribute_id",related_name = "attribute_image_ids")
    flavor_id = models.ForeignKey(ProductFlavors,verbose_name="Flavor",
                                  db_column="flavor_id",related_name = "flavor_attribute_image_ids")
    aboutus_banner = models.NullBooleanField(verbose_name = "Is About us Banner ?")
    contactus_banner = models.NullBooleanField(verbose_name = "Is Contact us Banner ?")
    customerreview_banner = models.NullBooleanField(verbose_name = "Is Contact Review Banner ?")
    
    _DATABASE = "odoo"    
    class Meta:
        managed=False
        db_table = "s3_object"   

class ProductTab(models.Model):
    id = models.IntegerField(primary_key=True)
    tab_style = models.CharField(max_length=20,verbose_name="Tab Style",choices = _TAB_STYLES)
    vol_id = models.ForeignKey(ProductAttributeValue,verbose_name = "Volume",blank=False,
                                     db_column="vol_id",
                                     related_name="tab_ids")
    consumable_stockable = models.CharField(max_length=20,verbose_name="Product Type",choices = _PRODUCT_TYPES)
    visible_all_customers = models.NullBooleanField(verbose_name="Visible to all customers")
    active = models.NullBooleanField(verbose_name="Active")
    specific_customer_ids = models.ManyToManyField(Partner,db_table="product_tab_res_partners",related_name="tab_ids")
    
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

    def get_name(self):
        name = ""
        if self.flavor_id and self.vol_id and self.conc_id:
            name = " | ".join([self.flavor_id.name,self.vol_id.name,self.conc_id.name])
        else:
            name = self.product_tmpl_id.name 
        return name

    def get_image_url(self):
        url = os.path.join(settings.STATIC_URL,settings.PLACEHOLDER_PRODUCT_IMAGE)
        if self.file_name:
            url = create_aws_url(self._meta.db_table,str(self.id))
        return url 

    def get_url(self):
        flavor_link = self.flavor_id.get_url()
        data = {'volume_id':self.vol_id.id}
        product_url = "?".join([flavor_link,urlencode(data)])
        return product_url
    
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
    create_date = models.DateTimeField(auto_now_add=True)
    write_date = models.DateTimeField(auto_now=True)
    write_uid = models.IntegerField('Write UID')
    create_uid = models.IntegerField('Write UID')
    name = models.CharField(verbose_name='Name',max_length=100)
    email = models.EmailField(verbose_name='Email ID')
    title = models.CharField(verbose_name='Title',max_length=200)
    description = models.TextField(verbose_name='Description')
    flavor_id = models.ForeignKey(ProductFlavors,verbose_name = "Flavor",db_column="flavor_id",blank=False,related_name = "flavor_review_ids")
    partner_id = models.ForeignKey(Partner,verbose_name='Customer',db_column="partner_id",related_name="review_ids")
    rating = models.CharField(verbose_name = "Rating",max_length=20,choices = _RATING)        

    _DATABASE = "odoo"
    class Meta:
        managed=False
        db_table = "flavor_reviews"          
            
        
            
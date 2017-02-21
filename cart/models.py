from __future__ import unicode_literals
from django.db import models
from catalog.models import ProductVariant
from helper import get_price
import uuid
from django.conf import settings
from django.core.urlresolvers import reverse

class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    cart_id = models.UUIDField(default=uuid.uuid4, editable=False)
    create_date = models.DateTimeField(auto_now_add=True)
    write_date = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=1)
    product_id = models.IntegerField(verbose_name="Product",blank=False)
    user_id = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name="User",blank=True,
                                db_column="user_id",
                                related_name="user_cart_item_ids",null=True)
    class Meta:
        db_table = "cart_items"
        ordering = ("create_date",)
    
    @property
    def get_product_url(self):
        if self.product:
            return self.product.get_url()
        return "#" 

    @property
    def get_price(self):
        if self.user_id:
            pass
        else:
            return self.product.vol_id.msrp
            
    @property
    def product(self):
        return ProductVariant.objects.get(id=self.product_id)
    
    @property       
    def get_total(self):
        price = self.get_price
        total = self.quantity * price
        return total    

    def name(self,product):
        return product.product_tmpl_id.name
     
    def augment_quantity(self,quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()
    
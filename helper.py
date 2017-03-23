from django.conf import settings
import os
from django.http import Http404

def get_product_variants(flavor,volume_id,type='product',sellable=True,purchasable=False):
    return flavor.flavor_product_variant_ids.filter(
                                                active=True,
                                                vol_id = volume_id,
                                                product_tmpl_id__type = 'product',
                                                product_tmpl_id__sale_ok=sellable,
                                                tab_id__vol_id=volume_id,
                                                tab_id__visible_all_customers=True,
                                                tab_id__consumable_stockable = 'product',
                                                tab_id__active = True).distinct('conc_id__id')

def is_user_business(user):
    if (not user.is_authenticated) or (not user.odoo_user.partner_id.classify_finance) or (user.odoo_user.partner_id.classify_finance == 'website'):
        return False
    else :
        return True    

def get_price(authenticated,volume,user=None,flavor=None):
    # volume,user,flavor are not ids but instances of the model
    if authenticated:
        pass
    else:
        return volume.msrp

def create_aws_url(key,fname):
    return os.path.join(settings.AWS_BASE_URL,settings.BUCKET,key,fname)

def safe_cast(func):
    def wrapper(self,request,id,template_name):
        try:
            return func(self,request,id,template_name)
        except (ValueError,TypeError) as e:
            raise Http404("Sorry the URL could not be found!")
        except AssertionError as e:
            raise Http404(e)
    return wrapper
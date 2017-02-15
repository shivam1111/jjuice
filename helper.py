from django.conf import settings
import os
from django.http import Http404

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
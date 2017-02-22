from django.db import models
from odoo.models import ResUsers
from django.contrib.auth.models import AbstractUser


class OdooUser(AbstractUser):
    REQUIRED_FIELDS = ['odoo_id','email']

    odoo_id = models.BigIntegerField(blank=False,null=False,verbose_name = "Odoo ID",unique=True)
    
    @property
    def odoo_user(self):
        try:
            return ResUsers.objects.get(id=self.odoo_id)
        except ResUsers.DoesNotExist:
            return None
        
        
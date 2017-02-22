from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib import admin
from models import OdooUser

class OdooUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Odoo'),{'fields':('odoo_id',)}),
    )    

admin.site.register(OdooUser, OdooUserAdmin)    
def global_context(request):
    from odoo.models import IrConfigParameters
    
    return {
            'site_name': IrConfigParameters.objects.get_param('site_name'),
            'meta_keywords': IrConfigParameters.objects.get_param('meta_keywords'),
            'meta_description': IrConfigParameters.objects.get_param('meta_description'),
        }
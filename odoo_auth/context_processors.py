def global_context(request):
    odoo_user = None
    if request.user.is_authenticated():
        odoo_user = request.user.odoo_user
    return {
            'odoo_user':odoo_user,
        }
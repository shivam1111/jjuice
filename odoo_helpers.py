from xmlrpclib import ServerProxy
from django.conf import settings
import logging

db_logger = logging.getLogger('db')
stdlogger = logging.getLogger('console')

def get_login_details():
    return {
            'url':settings.ODOO_URL,
            'username':settings.ODOO_USERNAME,
            'password':settings.ODOO_PASSWORD,
            'db':settings.ODOO_DB,
        }

def authenticate(username,url,db, password, context=None):
    if context==None:context={}
    common = ServerProxy('{}/xmlrpc/2/common'.format(url),allow_none=True)
    uid = common.authenticate(db, username, password, {})
    return uid

def get_login_authenticate():
    login_details = get_login_details()
    uid = authenticate(**login_details)
    if not uid:
        db_logger.error("The Odoo credentials set in Admin Config are incorrect")
    return login_details,uid


class OdooAdapter(object):
    login_details,uid = get_login_authenticate()
    models = ServerProxy('{}/xmlrpc/2/object'.format(login_details.get('url','')),allow_none=True)
    
    def execute_method(self,model,function_name,params_list=[],**kwargs):
        '''    
            **kwargs =send the dictionary of arguments but do not send uid parameter as it will be added by authentication
              params_list = You have an option if you want to send list of params or named params in kwargs. 
              
              Note: Make sure not mix parameters of kwargs with params_list 
        '''
        res = None
        try:
            if self.uid:
                models = ServerProxy('{}/xmlrpc/2/object'.format(self.login_details.get('url','')),allow_none=True)
                res = models.execute_kw(self.login_details.get('db',''), self.uid, self.login_details.get('password',''),model,function_name,params_list,kwargs)
        except Exception as e:
            stdlogger.exception(e)
            db_logger.exception(e)
        return res
    
    def create(self,model=False,vals={},context=None):
        assert model != False
        if context == None:context={}
        res = self.execute_method(model,'create',[vals,context])
        return res        
    
    def search_read(self,model=False,domain=None, fields=None, offset=0, limit=None, order=None, context=None):
        assert model != False
        if context == None:context={}
        res = self.execute_method(model,'search_read',[domain,fields,offset,limit,order,context])
        return res
    
    def read(self,ids,model=False,fields=[],context=None):
        assert model != False
        if context==None:context={}
        res = self.execute_method(model,'read',[],**{
                                     'ids':ids,
                                     'fields':fields,
                                     'context':context,
                                     })
        return res


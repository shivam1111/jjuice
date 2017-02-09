class OdooRouter(object):

    def db_for_read(self, model, **hints):
        database = getattr(model, "_DATABASE", None)
        if database:
            return database
        else:
            return "default"
        
    def db_for_write(self,model,**hints):
        database = getattr(model, "_DATABASE", None)
        if database:
            return database
        else:
            return "default"        

    def allow_relation(self, obj1, obj2, **hints):
        """
        Relations between objects are allowed if both objects are
        in the master/slave pool.
        """
        db_list = ('default')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None


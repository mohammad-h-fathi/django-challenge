
class MatchesDBRouter(object):
    """
    A router to control app1 db operations
    """

    def validate_db(self, model):
        from django.conf import settings
        if not 'matches' in settings.DATABASES:
            return None
        if model._meta.app_label == 'matches':
            return 'matches'

    def db_for_read(self, model, **hints):
        return self.validate_db(model)

    def db_for_write(self, model, **hints):
        return self.validate_db(model)

    def allow_relation(self, obj1, obj2, **hints):
        from django.conf import settings
        if not 'matches' in settings.DATABASES:
            return None
        if obj1._meta.app_label == 'matches' or obj2._meta.app_label == 'matches':
            return True
        return None

    def allow_syncdb(self, db, model):
        my_db = self.validate_db(model)
        if db == my_db:
            return model._meta.app_label == 'matches'
        elif model._meta.app_label == 'matches':
            return False
        return None

from django.apps import AppConfig


class ApisRelations2Config(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = 'apis_relations2'

    def ready(self):
        from . import signals

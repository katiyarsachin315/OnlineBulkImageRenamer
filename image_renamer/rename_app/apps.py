from django.apps import AppConfig


class RenameAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rename_app'

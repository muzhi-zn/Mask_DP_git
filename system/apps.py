from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules
from django.conf import settings

class SystemConfig(AppConfig):
    name = 'system'

    def ready(self):
        autodiscover_modules('load_white')


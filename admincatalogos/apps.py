from django.apps import AppConfig


class AdmincatalogosConfig(AppConfig):
    name = 'admincatalogos'

    def ready(self):
        import admincatalogos.signals
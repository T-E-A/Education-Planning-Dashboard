from django.apps import AppConfig


class DataapiappConfig(AppConfig):
    """
    Returns: none, configures the API_Elements app with BigAutoField as the default primary key type
    Args: none
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'API_Elements'

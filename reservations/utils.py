__author__ = 'jason.a.parent@gmail.com (Jason Parent)'

# Django imports...
from django.conf import settings

# Local imports...
from .models import Config


def get_param(param_name, default=None):
    try:
        param_value = Config.objects.first().data[param_name]
    except KeyError:
        return getattr(settings, param_name, default)
    else:
        return param_value
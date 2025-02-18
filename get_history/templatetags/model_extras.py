from django import template
from django.contrib.contenttypes.models import ContentType

register = template.Library()

@register.filter
def model_name(instance):
    try:
        return ContentType.objects.get_for_model(instance).model
    except ContentType.DoesNotExist:
        return 'Unknown Model'
    
@register.filter
def instance_name(instance):
    return str(instance)

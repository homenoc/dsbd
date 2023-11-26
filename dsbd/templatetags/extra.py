from django import template
from django.conf import settings
import markdown as md
from pytz import timezone

register = template.Library()


@register.simple_tag
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])


@register.simple_tag
def url_replace(request, **kwargs):
    params = request.GET.copy()
    for k, v in kwargs.items():
        params[k] = v
    return params.urlencode()


@register.simple_tag
def time_to_str(time):
    if time is None:
        return "無期限"
    time_format = "%Y/%m/%d %H:%M:%S"
    return time.astimezone(timezone(settings.TIME_ZONE)).strftime(time_format)


@register.simple_tag
def to_int(value):
    if not value:
        return None
    return int(value)


@register.simple_tag
def beta():
    return settings.BETA


@register.simple_tag
def debug():
    return settings.DEBUG


@register.simple_tag
def array_to_str(data):
    return ', '.join(data)


@register.simple_tag
def get_version():
    version = "develop"
    return version

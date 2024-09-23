import markdown as md
from django import template
from django.conf import settings
from pytz import timezone

register = template.Library()


@register.simple_tag
def markdown(value) -> str:
    return md.markdown(value, extensions=["markdown.extensions.fenced_code"])


@register.simple_tag
def url_replace(request, **kwargs) -> str:
    params = request.GET.copy()
    for k, v in kwargs.items():
        params[k] = v
    return params.urlencode()


@register.simple_tag
def time_to_str(time) -> str:
    if time is None:
        return "無期限"
    time_format = "%Y/%m/%d %H:%M:%S"
    return time.astimezone(timezone(settings.TIME_ZONE)).strftime(time_format)


@register.simple_tag
def to_int(value) -> int:
    if not value:
        return None
    return int(value)


@register.simple_tag
def beta() -> bool:
    return settings.BETA


@register.simple_tag
def debug() -> bool:
    return settings.DEBUG


@register.simple_tag
def array_to_str(data) -> str:
    return ", ".join(data)


@register.simple_tag
def get_version() -> str:
    version = "develop"
    return version


@register.simple_tag
def get_usage_url() -> str:
    return settings.USAGE_URL


@register.simple_tag
def get_privacy_policy_url() -> str:
    return settings.PRIVACY_POLICY_URL


@register.simple_tag
def get_fee_url() -> str:
    return settings.FEE_URL


@register.simple_tag
def is_admin_mode() -> bool:
    return settings.ADMIN_MODE

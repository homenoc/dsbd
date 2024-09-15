from django.conf import settings
from django.urls import reverse


def get_admin_url(instance) -> str:
    """
    任意のモデルインスタンスの管理ページURLを生成する。
    """
    model_name = instance._meta.model_name
    app_label = instance._meta.app_label
    admin_url = reverse(f"admin:{app_label}_{model_name}_change", args=[instance.pk])

    # フルURLにするために現在のサイトドメインを取得
    full_admin_url = f"{settings.ADMIN_DOMAIN_URL}{admin_url}"

    return full_admin_url


def get_admin_history_url(instance) -> str:
    """
    任意のモデルインスタンスの管理ページURLを生成する。
    """
    model_name = instance._meta.model_name
    app_label = instance._meta.app_label
    admin_url = reverse(f"admin:{app_label}_{model_name}_history", args=[instance.pk])

    # フルURLにするために現在のサイトドメインを取得
    admin_history_url = f"{settings.ADMIN_DOMAIN_URL}{admin_url}"

    return admin_history_url

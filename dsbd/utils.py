from django.conf import settings


def get_admin_url(instance) -> str:
    """
    任意のモデルインスタンスの管理ページURLを生成する。
    """
    model_name = instance._meta.model_name
    app_label = instance._meta.app_label

    # フルURLにするために現在のサイトドメインを取得
    full_admin_url = f"{settings.ADMIN_DOMAIN_URL}/admin/{app_label}/{model_name}/{instance.pk}/change/"

    return full_admin_url


def get_admin_history_url(instance) -> str:
    """
    任意のモデルインスタンスの管理ページURLを生成する。
    """
    model_name = instance._meta.model_name
    app_label = instance._meta.app_label

    # フルURLにするために現在のサイトドメインを取得
    admin_history_url = f"{settings.ADMIN_DOMAIN_URL}/admin/{app_label}/{model_name}/{instance.pk}/history/"

    return admin_history_url

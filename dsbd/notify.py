from django.conf import settings
from slack_sdk import WebhookClient

from dsbd.utils import get_admin_history_url, get_admin_url


def notify_delete_db(model_name: str, instance):
    admin_history_url = get_admin_history_url(instance)

    message = f"レコードが削除されました:\n{instance}"
    client = WebhookClient(settings.SLACK_WEBHOOK_LOG)
    client.send(
        attachments=[
            {
                "color": "danger",
                "title": "[%s]" % f"{model_name}",
                "text": f"{message}\n管理画面(履歴): {admin_history_url}",
            }
        ],
    )


def notify_insert_db(model_name: str, instance):
    admin_url = get_admin_url(instance)
    admin_history_url = get_admin_history_url(instance)

    message = f"新しいレコードが登録されました:\n{instance}"
    client = WebhookClient(settings.SLACK_WEBHOOK_LOG)
    client.send(
        attachments=[
            {
                "color": "good",
                "title": "[%s]" % f"{model_name}",
                "text": f"{message}\n管理画面: {admin_url}\n管理画面(履歴): {admin_history_url}",
            }
        ],
    )


def notify_update_db(model_name: str, instance):
    admin_url = get_admin_url(instance)
    admin_history_url = get_admin_history_url(instance)

    history = instance.history.all()
    if history.count() < 2:
        return  # 履歴が2つ未満の場合は差分がないため、何もしない

    latest = history.first()  # 最新の履歴
    previous = history[1]  # 直前の履歴

    changes = []

    # フィールドごとの差分を確認
    for field in instance._meta.fields:
        field_name = field.name
        old_value = getattr(previous, field_name, None)
        new_value = getattr(latest, field_name, None)

        if old_value != new_value:
            changes.append(f"{field_name}: {old_value} -> {new_value}")

    if changes:
        message = f"モデル '{instance}' の以下のフィールドが変更されました:\n" + "\n".join(changes)
        client = WebhookClient(settings.SLACK_WEBHOOK_LOG)
        client.send(
            attachments=[
                {
                    "color": "good",
                    "title": "[%s]" % f"{model_name}",
                    "text": f"{message}\n管理画面: {admin_url}\n管理画面(履歴): {admin_history_url}",
                }
            ],
        )


def notice_payment(metadata_type="", event_type="", data=None):
    client = WebhookClient(settings.SLACK_WEBHOOK_LOG)
    client.send(
        text="[%s(%s)] %s-%s [%d円(/%s)]"
        % (metadata_type, event_type, data["id"], data["name"], data["plan_amount"], data["plan_interval"]),
        attachments=[
            {
                "color": get_color(event_type),
                "title": "[%s(%s)] %s-%s" % (metadata_type, event_type, data["id"], data["name"]),
                "text": "%s-%s\namount: %d(%s)\nstatus: %s"
                % (data["start"], data["end"], data["plan_amount"], data["plan_interval"], data["status"]),
            }
        ],
    )


def get_color(status):
    match status:
        case "customer.subscription.created":
            return "warning"
        case "customer.subscription.updated":
            return "good"
        case "customer.subscription.deleted":
            return "danger"

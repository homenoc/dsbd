from django.conf import settings
from slack_sdk import WebhookClient


def notify_db_save(table_name="", type=0, data=""):
    event_name = "create"
    color = "good"
    if type == 1:
        event_name = "update"
    if type == 2:
        event_name = "delete"
        color = "danger"
    client = WebhookClient(settings.SLACK_WEBHOOK_LOG)
    client.send(
        text="[%s(%s)]" % (table_name, event_name),
        attachments=[
            {
                "color": color,
                "title": "[%s(%s)]" % (table_name, event_name),
                "text": "%s" % (data,)
            }
        ])


def notice_payment(metadata_type="", event_type="", data=None):
    client = WebhookClient(settings.SLACK_WEBHOOK_LOG)
    client.send(
        text="[%s(%s)] %s-%s [%d円(/%s)]" % (
            metadata_type,
            event_type,
            data['id'],
            data['name'],
            data['plan_amount'],
            data['plan_interval']
        ),
        attachments=[
            {
                "color": get_color(event_type),
                "title": "[%s(%s)] %s-%s" % (metadata_type, event_type, data['id'], data['name']),
                "text": "%s-%s\namount: %d(%s)\nstatus: %s" % (
                    data['start'],
                    data['end'],
                    data['plan_amount'],
                    data['plan_interval'],
                    data['status']
                )
            }
        ])


def get_color(status):
    if status == "customer.subscription.created":
        return "warning"
    elif status == "customer.subscription.updated":
        return "good"
    elif status == "customer.subscription.deleted":
        return "danger"

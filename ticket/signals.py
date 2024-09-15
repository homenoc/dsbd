from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from django.template.loader import render_to_string

from dsbd.notify import notify_delete_db, notify_insert_db, notify_update_db
from ticket.models import Chat, Ticket
from ticket.utils import get_user_lists


@receiver(pre_save, sender=Ticket)
def ticket_model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Ticket.objects.get(pk=instance.pk)
    except Ticket.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(post_save, sender=Ticket)
def post_ticket(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=Ticket)
def delete_ticket(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)


@receiver(pre_save, sender=Chat)
def chat_model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Chat.objects.get(pk=instance.pk)
    except Chat.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(post_save, sender=Chat)
def post_chat(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        subject = "[HomeNOC Dashboard System]新着のメッセージがあります"
        for user_list in get_user_lists(instance.ticket):
            message = render_to_string(
                "mail/ticket/message.txt",
                {
                    "username": user_list.username,
                    "ticket_id": instance.ticket.id,
                    "ticket_title": instance.ticket.title,
                    "message": instance.body,
                },
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_list.email], fail_silently=False)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=Chat)
def delete_chat(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)

from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from dsbd.notify import notify_db_save
from ticket.models import Chat, Ticket
from ticket.tool import SignalTool


@receiver(pre_save, sender=Ticket)
def ticket_model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Ticket.objects.get(pk=instance.pk)
    except Ticket.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(post_save, sender=Ticket)
def post_ticket(sender, instance, created, **kwargs):
    if created:
        text = SignalTool().get_create_ticket(True, instance)
        notify_db_save(table_name="Ticket", type=0, data=text)
    else:
        text = SignalTool().get_update_ticket(instance._pre_save_instance, instance)
        notify_db_save(table_name="Ticket", type=1, data=text)


@receiver(pre_delete, sender=Ticket)
def delete_ticket(sender, instance, **kwargs):
    text = SignalTool().get_create_ticket(False, instance)
    notify_db_save(table_name="Ticket", type=2, data=text)


@receiver(pre_save, sender=Chat)
def chat_model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Chat.objects.get(pk=instance.pk)
    except Chat.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(post_save, sender=Chat)
def post_chat(sender, instance, created, **kwargs):
    if created:
        text = SignalTool().get_create_chat(True, instance)
        notify_db_save(table_name="Chat", type=0, data=text)
    else:
        text = SignalTool().get_update_chat(instance._pre_save_instance, instance)
        notify_db_save(table_name="Chat", type=1, data=text)


@receiver(pre_delete, sender=Chat)
def delete_chat(sender, instance, **kwargs):
    text = SignalTool().get_create_chat(False, instance)
    notify_db_save(table_name="Chat", type=2, data=text)

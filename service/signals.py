from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from dsbd.notify import notify_delete_db, notify_insert_db, notify_update_db
from service.models import Connection, Service


@receiver(post_save, sender=Service)
def post_service(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=Service)
def delete_service(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)


@receiver(post_save, sender=Connection)
def post_connection(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=Connection)
def delete_connection(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)

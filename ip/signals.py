from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from dsbd.notify import notify_delete_db, notify_insert_db, notify_update_db
from ip.models import IP, IPJPNICUser, JPNICUser


@receiver(post_save, sender=JPNICUser)
def post_jpnic_user(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=JPNICUser)
def delete_jpnic_user(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)


@receiver(post_save, sender=IP)
def post_ip(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=IP)
def delete_ip(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)


@receiver(post_save, sender=IPJPNICUser)
def post_ip_jpnic_user(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=IPJPNICUser)
def delete_ip_jpnic_user(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)

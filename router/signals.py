from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from dsbd.notify import notify_delete_db, notify_insert_db, notify_update_db
from router.models import TunnelIP, TunnelRouter


@receiver(post_save, sender=TunnelRouter)
def post_tunnel_router(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=TunnelRouter)
def delete_tunnel_router(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)


@receiver(post_save, sender=TunnelIP)
def post_tunnel_ip(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=TunnelIP)
def delete_tunnel_ip(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)

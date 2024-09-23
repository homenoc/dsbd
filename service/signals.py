from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from custom_auth.models import Group
from dsbd.notify import notify_delete_db, notify_insert_db, notify_update_db
from service.models import Connection, Service


@receiver(post_save, sender=Service)
def service_model_post_save(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        # Group側の「サービス追加許可」、「JPNIC情報追加許可」をFalseにする
        Group.objects.filter(id=instance.group_id).update(allow_service_add=False, allow_jpnic_add=False)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=Service)
def service_model_pre_delete(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)


@receiver(post_save, sender=Connection)
def connection_model_post_save(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        # service側の「接続追加許可」をFalseにする
        Service.objects.filter(id=instance.service_id).update(allow_connection_add=False)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=Connection)
def connection_model_pre_delete(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)

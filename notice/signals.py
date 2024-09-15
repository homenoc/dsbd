from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from dsbd.notify import notify_delete_db, notify_insert_db, notify_update_db
from notice.models import Notice


@receiver(post_save, sender=Notice)
def post_notice(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=Notice)
def delete_notice(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)

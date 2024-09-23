from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from custom_auth.models import Group, User, UserGroup
from dsbd.notify import notify_delete_db, notify_insert_db, notify_update_db


@receiver(pre_save, sender=User)
def user_model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(post_save, sender=User)
def user_model_post_save(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_insert_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=User)
def user_model_pre_delete(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)


@receiver(pre_save, sender=Group)
def group_model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Group.objects.get(pk=instance.pk)
    except Group.DoesNotExist:
        instance._pre_save_instance = instance
    # 審査NG => 審査OKの場合にサービス追加とJPNIC追加を出来るようにする
    if not instance._pre_save_instance.is_pass and instance.is_pass:
        instance.allow_service_add = True
        instance.allow_jpnic_add = True

    # Statusが1以外の場合はサービス追加とJPNIC追加を禁止する
    if instance.status != 1:
        instance.allow_service_add = False
        instance.allow_jpnic_add = False


@receiver(post_save, sender=Group)
def group_model_post_save(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return

    notify_update_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=Group)
def group_model_pre_delete(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)


@receiver(post_save, sender=UserGroup)
def user_group_model_post_save(sender, instance, created, **kwargs):
    if created:
        notify_insert_db(model_name=sender.__name__, instance=instance)
        return
    notify_insert_db(model_name=sender.__name__, instance=instance)


@receiver(pre_delete, sender=UserGroup)
def user_group_model_pre_delete(sender, instance, **kwargs):
    notify_delete_db(model_name=sender.__name__, instance=instance)

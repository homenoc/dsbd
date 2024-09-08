from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from custom_auth.models import Group, User
from custom_auth.tool import SignalTool
from dsbd.notify import notify_db_save


@receiver(pre_save, sender=User)
def user_model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = User.objects.get(pk=instance.pk)
    except User.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(post_save, sender=User)
def post_user(sender, instance, created, **kwargs):
    if created:
        text = SignalTool().get_create_user(True, instance)
        notify_db_save(table_name="User", type=0, data=text)
    else:
        text = SignalTool().get_update_user(instance._pre_save_instance, instance)
        notify_db_save(table_name="User", type=1, data=text)


@receiver(pre_delete, sender=User)
def delete_user(sender, instance, **kwargs):
    text = SignalTool().get_create_user(False, instance)
    notify_db_save(table_name="User", type=2, data=text)


@receiver(post_save, sender=Group)
def update_group(sender, instance, created, **kwargs):
    # 審査OKステータス変更時にサービス追加許可にする
    if instance.is_pass and not instance.allow_service_add:
        instance.allow_service_add = True
        instance.save(update_fields=["allow_service_add"])
    # 審査NGステータス変更時にサービス追加拒否設定にする
    if not instance.is_pass and instance.allow_service_add:
        instance.allow_service_add = False
        instance.save(update_fields=["allow_service_add"])

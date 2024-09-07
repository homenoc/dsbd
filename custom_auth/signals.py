from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from custom_auth.models import User
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
        text = get_create_user(True, instance)
        notify_db_save(table_name="User", type=0, data=text)
    else:
        text = get_update_user(instance._pre_save_instance, instance)
        notify_db_save(table_name="User", type=1, data=text)


@receiver(pre_delete, sender=User)
def delete_user(sender, instance, **kwargs):
    text = get_create_user(False, instance)
    notify_db_save(table_name="User", type=2, data=text)


def get_create_user(short, instance):
    text = "--%d[%s]--\n" % (
        instance.id,
        instance.username,
    )
    return text if not short else text + "有効: %r\nE-Mail: %s\n" % (instance.is_active, instance.email)


def get_update_user(before, after):
    text = "%s----更新状況----\n" % (get_create_user(True, before),)
    if before.username != after.username:
        text += "username: %s => %s\n" % (before.username, after.username)
    if before.username_jp != after.username_jp:
        text += "username(jp): %s => %s\n" % (before.username, after.username)
    if before.email != after.email:
        text += "E-Mail: %s => %s\n" % (before.email, after.email)
    if before.is_active != after.is_active:
        text += "有効: %r => %r\n" % (before.is_active, after.is_active)
    text += "------------\n"
    return text


def get_create_signup_key(short, instance):
    text = "--%d[%s]--\n" % (
        instance.id,
        instance.key,
    )
    return text if not short else text + "利用済み: %r\n有効期限: %s\n" % (instance.is_used, instance.expired_at)


def get_update_signup_key(before, after):
    text = "%s----更新状況----\n" % (get_create_signup_key(True, before),)
    if before.key != after.key:
        text += "key: %s => %s\n" % (before.key, after.key)
    if before.is_used != after.is_used:
        text += "使用済み: %r => %r\n" % (before.is_used, after.is_used)
    if before.expired_at != after.expired_at:
        text += "有効期限: %s => %s\n" % (before.expired_at, after.expired_at)
    if before.comment != after.comment:
        text += "comment: %r => %r\n" % (before.comment, after.comment)
    text += "------------\n"
    return text

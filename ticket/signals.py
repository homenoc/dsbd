from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver

from dsbd.notify import notify_db_save
from ticket.models import Ticket, Chat


@receiver(pre_save, sender=Ticket)
def ticket_model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Ticket.objects.get(pk=instance.pk)
    except Ticket.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(post_save, sender=Ticket)
def post_ticket(sender, instance, created, **kwargs):
    if created:
        text = get_create_ticket(True, instance)
        notify_db_save(table_name="Ticket", type=0, data=text)
    else:
        text = get_update_ticket(instance._pre_save_instance, instance)
        notify_db_save(table_name="Ticket", type=1, data=text)


@receiver(pre_delete, sender=Ticket)
def delete_ticket(sender, instance, **kwargs):
    text = get_create_ticket(False, instance)
    notify_db_save(table_name="Ticket", type=2, data=text)


def get_create_ticket(short, instance):
    text = '--%d[%s]--\nUser: %s| Group: %s\n' % (instance.id, instance.title, instance.user, instance.group)
    return text if not short else text + 'title: %s\nbody: %s\n解決済み: %s\n承認済み: %s\n拒否済み: %s\n運営委員から起票: %s\n' % (
        instance.title, instance.body, solved_to_str(instance.is_solved), approve_to_str(instance.is_approve),
        reject_to_str(instance.is_reject), from_admin_to_str(instance.from_admin))


def get_update_ticket(before, after):
    text = '%s----更新状況----\n' % (get_create_ticket(True, before),)
    if before.user != after.user:
        text += 'user: %s => %s\n' % (before.user, after.user)
    if before.group != after.group:
        text += 'group: %s => %s\n' % (before.group, after.group)
    if before.title != after.title:
        text += 'title: %s => %s\n' % (before.title, after.title)
    if before.body != after.body:
        text += 'body: %s => %s\n' % (before.body, after.body)
    if before.is_solved != after.is_solved:
        text += '解決済み: %s => %s\n' % (solved_to_str(before.is_solved), solved_to_str(after.is_solved))
    if before.is_approve != after.is_approve:
        text += '承認済み: %s => %s\n' % (approve_to_str(before.is_approve), approve_to_str(after.is_approve))
    if before.is_reject != after.is_reject:
        text += '拒否済み: %s => %s\n' % (reject_to_str(before.is_reject), reject_to_str(after.is_reject))
    if before.from_admin != after.from_admin:
        text += '運営委員から起票: %s => %s\n' % (from_admin_to_str(before.from_admin), reject_to_str(after.from_admin))
    text += '------------\n'
    return text


def solved_to_str(is_solved):
    return '解決済み' if is_solved else '未解決'


def approve_to_str(is_approve):
    return '承認' if is_approve else '未承認'


def reject_to_str(is_reject):
    return '拒否済み' if is_reject else 'not 拒否'


def from_admin_to_str(from_admin):
    return '運営委員から起票' if from_admin else 'not 運営委員から起票'


@receiver(pre_save, sender=Chat)
def chat_model_pre_save(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = Chat.objects.get(pk=instance.pk)
    except Chat.DoesNotExist:
        instance._pre_save_instance = instance


@receiver(post_save, sender=Chat)
def post_chat(sender, instance, created, **kwargs):
    if created:
        text = get_create_chat(True, instance)
        notify_db_save(table_name="Chat", type=0, data=text)
    else:
        text = get_update_chat(instance._pre_save_instance, instance)
        notify_db_save(table_name="Chat", type=1, data=text)


@receiver(pre_delete, sender=Chat)
def delete_chat(sender, instance, **kwargs):
    text = get_create_chat(False, instance)
    notify_db_save(table_name="Chat", type=2, data=text)


def get_create_chat(short, instance):
    text = '--%d--\n[%s] User: %s| Group: %s\nTicket: %s\n' % (
        instance.id, 'ユーザ投稿' if instance.is_admin else '管理者投稿', instance.user, instance.group,
        instance.ticket)
    return text if not short else text + 'body: %s\n' % (instance.body,)


def get_update_chat(before, after):
    text = '%s----更新状況----\n' % (get_create_chat(True, before),)
    if before.user != after.user:
        text += 'user: %s => %s\n' % (before.user, after.user)
    if before.group != after.group:
        text += 'group: %s => %s\n' % (before.group, after.group)
    if before.body != after.body:
        text += 'body: %s => %s\n' % (before.body, after.body)
    if before.is_admin != after.is_admin:
        text += '運営委員回答: %s => %s\n' % (admin_to_str(before.is_admin), admin_to_str(after.is_admin))
    text += '------------\n'
    return text


def admin_to_str(is_admin):
    return '運営委員回答' if is_admin else 'not 運営委員回答'


def active_to_str(is_admin):
    return '有効' if is_admin else '無効'

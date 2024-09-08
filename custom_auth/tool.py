import random
import string


def random_string(num):
    random_list = [random.choice(string.ascii_letters + string.digits) for i in range(num)]
    return "".join(random_list)


class SignalTool:
    def get_create_user(self, short, instance):
        text = "--%d[%s]--\n" % (
            instance.id,
            instance.username,
        )
        return text if not short else text + "有効: %r\nE-Mail: %s\n" % (instance.is_active, instance.email)

    def get_update_user(self, before, after):
        text = "%s----更新状況----\n" % (self.get_create_user(True, before),)
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

    def get_create_signup_key(self, short, instance):
        text = "--%d[%s]--\n" % (
            instance.id,
            instance.key,
        )
        return text if not short else text + "利用済み: %r\n有効期限: %s\n" % (instance.is_used, instance.expired_at)

    def get_update_signup_key(self, before, after):
        text = "%s----更新状況----\n" % (self.get_create_signup_key(True, before),)
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

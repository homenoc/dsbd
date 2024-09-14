class SignalTool:
    def get_create_ticket(self, short, instance):
        text = "--%d[%s]--\nUser: %s| Group: %s\n" % (instance.id, instance.title, instance.user, instance.group)
        return (
            text
            if not short
            else text
            + "title: %s\nbody: %s\n解決済み: %s\n承認済み: %s\n拒否済み: %s\n運営委員から起票: %s\n"
            % (
                instance.title,
                instance.body,
                self.solved_to_str(instance.is_solved),
                self.approve_to_str(instance.is_approve),
                self.reject_to_str(instance.is_reject),
                self.from_admin_to_str(instance.from_admin),
            )
        )

    def get_update_ticket(self, before, after):
        text = "%s----更新状況----\n" % (self.get_create_ticket(True, before),)
        if before.user != after.user:
            text += "user: %s => %s\n" % (before.user, after.user)
        if before.group != after.group:
            text += "group: %s => %s\n" % (before.group, after.group)
        if before.title != after.title:
            text += "title: %s => %s\n" % (before.title, after.title)
        if before.body != after.body:
            text += "body: %s => %s\n" % (before.body, after.body)
        if before.is_solved != after.is_solved:
            text += "解決済み: %s => %s\n" % (self.solved_to_str(before.is_solved), self.solved_to_str(after.is_solved))
        if before.is_approve != after.is_approve:
            text += "承認済み: %s => %s\n" % (
                self.approve_to_str(before.is_approve),
                self.approve_to_str(after.is_approve),
            )
        if before.is_reject != after.is_reject:
            text += "拒否済み: %s => %s\n" % (self.reject_to_str(before.is_reject), self.reject_to_str(after.is_reject))
        if before.from_admin != after.from_admin:
            text += "運営委員から起票: %s => %s\n" % (
                self.from_admin_to_str(before.from_admin),
                self.reject_to_str(after.from_admin),
            )
        text += "------------\n"
        return text

    def solved_to_str(self, is_solved):
        return "解決済み" if is_solved else "未解決"

    def approve_to_str(self, is_approve):
        return "承認" if is_approve else "未承認"

    def reject_to_str(self, is_reject):
        return "拒否済み" if is_reject else "not 拒否"

    def from_admin_to_str(self, from_admin):
        return "運営委員から起票" if from_admin else "not 運営委員から起票"

    def get_create_chat(self, short, instance):
        text = "--%d--\n[%s] User: %s| Group: %s\nTicket: %s\n" % (
            instance.id,
            "ユーザ投稿" if instance.is_admin else "管理者投稿",
            instance.user,
            instance.group,
            instance.ticket,
        )
        return text if not short else text + "body: %s\n" % (instance.body,)

    def get_update_chat(self, before, after):
        text = "%s----更新状況----\n" % (self.get_create_chat(True, before),)
        if before.user != after.user:
            text += "user: %s => %s\n" % (before.user, after.user)
        if before.group != after.group:
            text += "group: %s => %s\n" % (before.group, after.group)
        if before.body != after.body:
            text += "body: %s => %s\n" % (before.body, after.body)
        if before.is_admin != after.is_admin:
            text += "運営委員回答: %s => %s\n" % (self.admin_to_str(before.is_admin), self.admin_to_str(after.is_admin))
        text += "------------\n"
        return text

    def admin_to_str(self, is_admin):
        return "運営委員回答" if is_admin else "not 運営委員回答"

    def active_to_str(self, is_admin):
        return "有効" if is_admin else "無効"


def get_user_lists(ticket):
    if ticket.group:
        return ticket.group.users.all()
    else:
        return [ticket.user]

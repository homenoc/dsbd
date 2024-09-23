def get_user_lists(ticket):
    if ticket.group:
        return ticket.group.users.all()
    else:
        return [ticket.user]

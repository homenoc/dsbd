import datetime
import json

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.utils import timezone

from ticket.models import Chat, Ticket


@sync_to_async()
def get_ticket(id):
    return Ticket.objects.filter(id=id).first()


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.ticket_id = None
        self.chat_group_name = None
        self.user = None
        self.group = 0

    @sync_to_async()
    def add_chat(self, message):
        if not self.group:
            Chat(user=self.user, ticket_id=self.ticket_id, body=message, is_admin=False).save()
        else:
            Chat(user=self.user, group_id=self.group, ticket_id=self.ticket_id, body=message, is_admin=False).save()

    @sync_to_async
    def check(self):
        ticket = Ticket.objects.filter(id=self.ticket_id).first()
        if ticket.group is None:
            if self.user.id != ticket.user.id:
                return False
        else:
            group_exists = False
            for group in self.user.groups.all():
                if group.id == ticket.group.id:
                    group_exists = True
            if not group_exists:
                return False
        return True

    @sync_to_async
    def get_ticket(self):
        ticket = Ticket.objects.filter(id=self.ticket_id).first()
        if ticket.group:
            self.group = ticket.group.id

    async def connect(self):
        self.ticket_id = int(self.scope["url_route"]["kwargs"]["ticket_id"])
        self.chat_group_name = f"chat_{self.ticket_id}"
        self.user = self.scope["user"]

        if not await self.check():
            await self.close()
            return

        await self.get_ticket()

        await self.accept()

        # JOIN CHAT Group
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.send(text_data="")

    async def disconnect(self, close_code):
        if self.ticket_id is None or self.chat_group_name:
            print("ERROR")
        # LEAVE CHAT Group
        await self.channel_layer.group_discard(self.chat_group_name, self.channel_name)
        pass

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.add_chat(message)

        time_format = "%Y/%m/%d %H:%M:%S"
        time = (
            datetime.datetime.now(tz=datetime.timezone.utc if settings.USE_TZ else None)
            .astimezone(timezone(settings.TIME_ZONE))
            .strftime(time_format)
        )

        await self.channel_layer.group_send(
            self.chat_group_name,
            {
                "type": "broadcast_message",
                "time": time,
                "user_id": self.user.id,
                "username": self.user.username,
                "group": self.group,
                "message": message,
                "is_admin": False,
            },
        )

    async def broadcast_message(self, event):
        time = event["time"]
        user_id = int(event["user_id"])
        username = event["username"]
        group = int(event["group"])
        message = event["message"]
        is_admin = event["is_admin"]
        if is_admin:
            username = ""
            group = 0

        await self.send(
            text_data=json.dumps(
                {
                    "time": time,
                    "user_id": user_id,
                    "username": username,
                    "group": group,
                    "message": message,
                    "is_admin": is_admin,
                }
            )
        )

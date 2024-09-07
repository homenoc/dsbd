import datetime
import json

from asgiref.sync import sync_to_async
from django.conf import settings
from django.utils import timezone

from ticket.consumers import ChatConsumer
from ticket.models import Chat, Ticket


@sync_to_async()
def get_ticket(id):
    return Ticket.objects.filter(id=id).first()


class AdminChatConsumer(ChatConsumer):
    @sync_to_async()
    def add_chat(self, message):
        Chat(user=self.user, ticket_id=self.ticket_id, body=message, is_admin=True).save()

    async def connect(self):
        self.ticket_id = int(self.scope["url_route"]["kwargs"]["ticket_id"])
        self.chat_group_name = f"chat_{self.ticket_id}"
        self.user = self.scope["user"]

        if not self.user.is_staff:
            await self.close()
            return

        await self.get_ticket()
        await self.accept()

        # JOIN CHAT Group
        await self.channel_layer.group_add(self.chat_group_name, self.channel_name)
        await self.send(text_data="")

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
                "group": 0,
                "message": message,
                "is_admin": True,
            },
        )

    async def broadcast_message(self, event):
        time = event["time"]
        user_id = int(event["user_id"])
        username = event["username"]
        group = int(event["group"])
        message = event["message"]
        is_admin = event["is_admin"]

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

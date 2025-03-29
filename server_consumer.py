from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from urllib.parse import parse_qs
import json

from accounts.models import User
from cpanels.models import OnlineTeachers
from .models import OnlineLectoureApps, UserDevicePreferences


class SupportConsumer(AsyncWebsocketConsumer):
    """Handles communication between paired React and device clients"""

    clients = {}  # {access_code: {'react_channel': ..., 'device_channel': ...}}

    async def connect(self):
        query_string = self.scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        access_code = params.get("access_code", [None])[0]
        client_type = params.get("client_type", ["device"])[0]

        if not access_code:
            await self.close()
            return

        if client_type == "react":
            self.clients = self.add_client_to_group(access_code, 'react_channel', self.channel_name)
            await self.channel_layer.group_add(access_code, self.channel_name)
            await self.accept()
        elif client_type == "device":
            self.clients = self.add_client_to_group(access_code, 'device_channel', self.channel_name)
            if await self.set_user_connected(access_code):
                await self.channel_layer.group_add(access_code, self.channel_name)
                await self.accept()
            else:
                await self.accept()
                await self.send(text_data=json.dumps(
                    {
                        "message_type": "INFO",
                        "message_content": f"There is no associated lectoure account with {access_code}",
                    }
                ))
                await self.close()

        print(f"\t\t\tconnected clients")
        print(f"\t\t\tclients: {self.__class__.clients}")


    async def disconnect(self, close_code):
        channel_type = None
        access_code = None

        # Identify whether the disconnected channel is react or device
        for ac, channels in self.clients.items():
            if channels.get('react_channel') == self.channel_name:
                channel_type = 'react_channel'
                access_code = ac
            elif channels.get('device_channel') == self.channel_name:
                channel_type = 'device_channel'
                access_code = ac

        if access_code and channel_type:
            if channel_type == "device_channel":
                await self.set_user_disconnected(access_code)
            self.remove_client_from_group(access_code, channel_type)
            await self.channel_layer.group_discard(access_code, self.channel_name)

        print(f"\t\t\tdisconnected clients")
        print(f"\t\t\tclients: {self.__class__.clients}")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except:
            data = {}

        message_type = data.get("message_type")
        access_code = data.get("access_code")
        client = data.get("client")


        if client == "react":
            class_id = data.get("class_id")
            class_type = data.get("class_type")
            lectoure_id = data.get("lectoure_id")

            if message_type in ("start_recording", "stop_recording"):
                channel_layer = get_channel_layer()
                device_channel_name = None
                print("f\n\n\treceived command\n")
                print(f"\n\n\tself.client: {self.clients}\n")
                print(f"\n\n\tself.client: {self.clients.get(access_code)}\n")
                if access_code in self.clients:
                    print("\n\n\n\taccess_code in self.clients\n")
                    device_channel_name = self.clients[access_code].get('device_channel')
                else:
                    print("\n\n\n\taccess_code is not self.clients\n")


                if not device_channel_name:
                    await self.send(text_data=json.dumps(
                        {"success": False, "message": "Client is not connected, Please make sure app is running and try again"}
                    ))
                else:
                    await channel_layer.send(
                        device_channel_name,
                        {
                            'type': "send_command_to_client",
                            'message_type': message_type,  # This calls the `chat_message` method in the consumer
                            'class_id': class_id,
                            'class_type': class_type,
                            'lectoure_id': lectoure_id,
                        }
                    )
            else:
                await self.send(text_data=json.dumps({'error': 'Unhandled message type received'}))
        elif client == "device":
            channel_layer = get_channel_layer()
            react_channel_name = None
            if access_code in self.clients:
                react_channel_name = self.clients[access_code].get('react_channel')

            if react_channel_name:
                await channel_layer.send(
                    react_channel_name,
                    {
                        'type': "send_command_to_react",
                        **data
                    }
                )

        else:
            # echo back
            await self.send(text_data=text_data)

    async def send_command_to_client(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def send_command_to_react(self, event):
        await self.send(text_data=json.dumps({**event}))

    async def forward_command_to_device(self, access_code, message_data):
        device_channel = self.clients.get(access_code, {}).get('device_channel')
        if device_channel:
            await self.channel_layer.send(device_channel, {
                'type': 'command.message',
                'message': message_data
            })
        else:
            await self.send(text_data=json.dumps({'status': 'No connected device'}))

    async def command_message(self, event):
        message = event['message']
        access_code = message['access_code']
        react_channel = self.clients.get(access_code, {}).get('react_channel')

        if react_channel:
            await self.channel_layer.send(react_channel, {
                'type': 'channel.message',
                'message': {'status': 'Command executed successfully', **message}
            })

    async def channel_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({'status': message}))

    def add_client_to_group(self, access_code, channel_type, channel_name):
        """Adds client to the maintained pairing data structure"""
        if access_code not in self.clients:
            self.clients[access_code] = {}
        self.clients[access_code][channel_type] = channel_name
        return self.clients

    def remove_client_from_group(self, access_code, channel_type):
        """Handles client disconnection and cleanup"""
        if access_code in self.clients and channel_type in self.clients[access_code]:
            del self.clients[access_code][channel_type]
            if not self.clients[access_code]:  # Remove the access code key if no more channels are associated
                del self.clients[access_code]

    @database_sync_to_async
    def set_user_connected(self, access_code):
        """Updates DB to save user status as connected (sync version)"""
        online_teacher = OnlineTeachers.objects.filter(user__access_code=access_code).first()
        if online_teacher:
            lectoure_app, is_created = OnlineLectoureApps.objects.get_or_create(lektor=online_teacher)
            lectoure_app.access_code = access_code
            lectoure_app.is_live = True
            lectoure_app.save()

            return True

    @database_sync_to_async
    def set_user_disconnected(self, access_code):
        """Updates DB to save user status as disconnected (sync version)"""
        online_teacher = OnlineTeachers.objects.filter(user__access_code=access_code).first()
        if online_teacher:
            lectoure_app, is_created = OnlineLectoureApps.objects.get_or_create(lektor=online_teacher)
            lectoure_app.access_code = access_code
            lectoure_app.is_live = False
            lectoure_app.save()


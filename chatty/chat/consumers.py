
from concurrent.futures import ThreadPoolExecutor
import asyncio
import logging
from typing import AsyncGenerator, AsyncIterable
import jsonpickle
from abc import ABC, abstractmethod
from asyncio.log import logger
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from django.db import transaction

from . import validators
from . import models


class BaseMessage(ABC):
    @abstractmethod
    async def persist(self):
        """Stores this message in the database. Returns True if successful."""
        raise NotImplementedError("Not implemented")


class ConsumerMessage(BaseMessage):
    @abstractmethod
    async def react_to_message(self, recipient_consumer: 'ChatConsumer' = None):
        raise NotImplementedError("Not implemented")


class ChatGroupTextMessage(ConsumerMessage):
    def __init__(self, username, message_text, room: 'str',):

        self.username = username
        self.message_text = message_text

        self.room_name = room
        self.persisted = False

    def sync_message_getter(cls, room_name):
        msg_dicts = []
        for msg in models.Message.objects.filter(room__room_name=room_name)[:25]:
            msg_dicts.append({
                'username': msg.user.username,
                'message_text': msg.message_body,
                'room': msg.room.room_name})
        return msg_dicts

    @sync_to_async
    def get_message_in_db_count(cls, room_name):
        print(int(models.Message.objects.filter(
            room__room_name=room_name).count()))
        return

    @classmethod
    async def get_chat_messages(cls, room_name: str) -> 'AsyncIterable[ChatGroupTextMessage]':
        """A generator that yields all stored chat messages"""
        message_dicts = await sync_to_async(cls.sync_message_getter)(cls,
                                                                     room_name)
        msg_count = await cls.get_message_in_db_count(room_name)

        for message_dict in message_dicts:
            user_message = ChatGroupTextMessage(
                username=message_dict.get('username'),
                message_text=message_dict.get('message_text'),
                room=message_dict.get('room'),
            )
            yield user_message

    async def react_to_message(self, recipient_consumer: 'ChatConsumer' = None):

        # room_members_count = await recipient_consumer.get_group_consumer_count(
        #     recipient_consumer.room_group_name)
        response_msg = {'username': self.username,
                        'message': self.message_text,
                        'room': self.room_name,
                        # 'no_of_room_members': room_members_count
                        }

        await recipient_consumer.send(text_data=json.dumps(response_msg))

    @sync_to_async
    def persist(self):
        if self.persisted:
            return True

        with transaction.atomic():
            try:
                user, created = models.User.objects.get_or_create(
                    username=self.username)
                room, created = models.Room.objects.get_or_create(
                    room_name=self.room_name)
                models.Message.objects.create(
                    room=room, message_body=self.message_text,
                    user=user,
                )
            except Exception as e:
                logger.error(str(e))
                return False
            self.persisted = True
            return True


# ----------------------------------------------------------------

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        username = self.scope['url_route']['kwargs']['username']
        room_name = self.scope['url_route']['kwargs']['room_name']

        sanitizer_username = validators.HtmlSanitizer(
            base_cleaner=validators.BasicCleaning(username)
        )
        sanitizer_room_name = validators.HtmlSanitizer(
            base_cleaner=validators.BasicCleaning(room_name)
        )

        username = sanitizer_username.clean()
        room_name = sanitizer_room_name.clean()
        validator = validators.ChannelGroupValidator()
        if not validator.is_valid(room_name) or not validator.is_valid(username):
            await self.close()
            return

        self.username = username
        self.room_name = room_name
        self.room_group_name = f"{room_name}"

        await self.channel_layer.group_add(self.room_group_name,
                                           self.channel_name)

        logger.info(
            f"Accepted connection to {self.username} in room {room_name}")
        await self.accept()

        async for chat_message in ChatGroupTextMessage.get_chat_messages(room_name):
            chat_message: 'ChatGroupTextMessage'
            await chat_message.react_to_message(self)

    async def disconnect(self, code):
        logger.info('Disconnecting with code %s', code)
        # await self.channel_layer.group_discard(self.room_group_name ,
        #                                        self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        message_json = json.loads(text_data)
        generic_message = ChatGroupTextMessage(
            username=message_json['username'],
            message_text=message_json['message'],
            room=self.room_name
        )
        await generic_message.persist()

        serialized_message = jsonpickle.encode(generic_message)
        # send message to all room members
        await self.channel_layer.group_send(self.room_group_name,
                                            {'type': 'group.message',
                                             'message': serialized_message})

    async def group_message(self, event):
        """Default recipient of every group messages"""
        logging.info("Group message received")
        consumer_message: 'ConsumerMessage' = jsonpickle.decode(
            event['message'])
        await consumer_message.react_to_message(recipient_consumer=self)

    # ----------------------------------------------------------------
    # Helpers

    # async def get_group_consumer_count(self, group_name):
    #     group_info = await self.channel_layer.group_channels(group_name)
    #     return len(group_info)

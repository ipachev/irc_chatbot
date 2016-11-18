import re
import sys
from enum import Enum

from unittest import TestCase


class Bot:
    def __init__(self, name):
        self.name = "{}{}".format(name, "-bot")
        self.pattern = re.compile(r"%s:\s?(.*)" % self.name)
        self.channel = None

    def connect(self, irc_channel):
        self.channel = irc_channel
        self.channel.connect(self.name)
        self.channel.add_message_callback(self.message_recieved)

    def message_recieved(self, message, source_user=""):
        print("RECEIVED MESSAGE", message)
        match = re.match(self.pattern, message)
        if match:
            text = self.get_text(match)
            if not self.special_message(text):
                reply = self.create_reply(source_user, text)
                if reply:
                    self.send_message(reply, source_user)

    def special_message(self, text):
        msg_type = MessageType.get_type(text)
        if msg_type == MessageType.normal:
            return False
        elif msg_type == MessageType.die:
            self.die()
        elif msg_type == MessageType.forget:
            self.forget()
        return True

    def get_text(self, match):
        return match.group(1)

    def create_reply(self, source_user, text):
        return "hi"

    def send_message(self, text, target_user=None):
        if target_user is not None:
            message = "{}: {}".format(target_user, text)
        else:
            message = text
        self.channel.send_message(message)

    def forget(self):
        #TODO: delete knowledge db
        pass

    def die(self):
        self.send_message("good bye cruel world")
        self.channel.disconnect()
        sys.exit(0)


class MessageType(Enum):
    normal = 0
    die = 1
    forget = 2

    @staticmethod
    def get_type(text):
        if text == "die":
            return MessageType.die
        elif text == "*forget":
            return MessageType.forget
        else:
            return MessageType.normal


class TestBot(TestCase):
    def setUp(self):
        self.bot = Bot("taco")

    def test_should_respond(self):
        message = "taco-bot: what's up?"
        self.bot.message_recieved("auser", message)

        message = "nottaco-bot: what's up?"
        self.bot.message_recieved("auser", message)
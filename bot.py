import re
import sys
from unittest import TestCase
from enum import Enum

class Bot:
    def __init__(self, name):
        self.name = "{}{}".format(name, "-bot")
        self.pattern = re.compile(r"%s:\s?(.*)" % self.name)
        self.channel = None

    def connect(self, irc_channel):
        #TODO irc stuff here
        self.channel = irc_channel

    def message_recieved(self, message, source_user):
        match = re.match(self.pattern, message)
        if match:
            text = self.get_text(match)
            if not self.special_message(text):
                reply = self.create_reply(source_user, text)
                if reply:
                    self.send_message(source_user, reply)

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

    def send_message(self, target_user, text):
        message = "{}: {}".format(target_user, text)
        self.channel.send(message)

    def forget(self):
        #TODO: delete knowledge db
        pass

    def die(self):
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
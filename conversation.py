from queue import Queue, Empty
from threading import Thread
from time import sleep
from random import uniform

from personalities.sheldon import Sheldon
from personalities.generic import Generic



class ConversationStateMachine:
    def __init__(self, partner_name, reply_sink, finish_hook=None, default_persona="generic"):
        """
        Creates a greeting state machine that handles the greeting of a conversation by producing replies.
        :param partner_name: Name of the person we're conversing with
        :param reply_sink: Function to call with outgoing messages (irc privmsg probably)
        :param start_state: Can either be State.outreach_reply or State.start. State.start will initiate the conversation,
        while State.outreach_reply will partake in a conversation already initiated by someone else.
        """
        self.sheldon = Sheldon(self.reply)
        self.generic = Generic(self.reply)
        self.active = self.generic if default_persona == "generic" else self.sheldon

        self.conversation_partner = partner_name
        self.message_queue = Queue()
        self.thread = Thread(target=self.loop)
        self.reply_sink = reply_sink
        self.finish_hook = finish_hook
        self.stopmsg = False

    def stop(self):
        self.stopmsg = True

    def start(self, initial_message=None):
        """
        Call this so start the greeting state machine
        """
        if not initial_message:
            self.active.initiate()
        else:
            self.message_queue.put(initial_message)
        self.thread.start()

    def incoming_message(self, message):
        """
        Insert a message into the queue that should be processed by this greeting state machine.
        :param message: The message to be processed
        """
        self.message_queue.put(message)

    def reply(self, message):
        """
        Sends a reply to the person this greeting state machine is conversing with using the reply sink.
        :param message: Message to be sent as a reply
        """
        outgoing_message = "{}: {}".format(self.conversation_partner, message)
        if not self.stopmsg:
            self.reply_sink(outgoing_message)

    def loop(self):
        while(not self.stopmsg):
            incoming_message = None
            try:
                incoming_message = self.message_queue.get(timeout=30)
                sleep(uniform(1, 3))
            except Empty:
                incoming_message = None
                self.active.handle_timeout()
            if self.active.delegate(incoming_message):
                if self.active is self.generic:
                    self.active = self.sheldon
                else:
                    self.active = self.sheldon
            if self.active.handle_message(incoming_message):
                break
        if self.finish_hook:
            self.finish_hook(self.conversation_partner)

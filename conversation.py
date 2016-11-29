from enum import IntEnum
from queue import Queue, Empty
from threading import Thread
from time import sleep
from random import uniform, choice
import re
import nltk.data

from lang import NounPhraseExtractor
from sheldon import Sheldon

import wikipedia

class State(IntEnum):
    start = 1
    initial_outreach = 2
    second_outreach = 3
    outreach_reply = 4
    inquiry = 5
    inquiry_reply = 6
    absorb = 7
    inquiry2 = 8
    inquiry_reply2 = 9
    give_up = 10
    end = 11
    free = 12


BasicResponses = {State.initial_outreach: ["hi","hello"],
    State.second_outreach: ["I said hi", "excuse me, hello?"],
    State.outreach_reply: ["hi", "hello back at you!"],
    State.inquiry: ["how are you?", "what’s happening?"],
    State.inquiry_reply: ["I’m good", "I’m fine"],
    State.absorb: None,
    State.inquiry2: ["how about you?", "and yourself?"],
    State.inquiry_reply2: ["I’m good", "I’m fine, thanks for asking"],
    State.give_up: ["Ok, forget you.", "Whatever. "]
    }

class ConversationStateMachine:
    def __init__(self, partner_name, reply_sink, finish_hook=None, start_state=State.start):
        """
        Creates a greeting state machine that handles the greeting of a conversation by producing replies.
        :param partner_name: Name of the person we're conversing with
        :param reply_sink: Function to call with outgoing messages (irc privmsg probably)
        :param start_state: Can either be State.outreach_reply or State.start. State.start will initiate the conversation,
        while State.outreach_reply will partake in a conversation already initiated by someone else.
        """
        self.sheldon = Sheldon()
        self.state = start_state
        self.conversation_partner = partner_name
        self.message_queue = Queue()
        self.thread = Thread(target=self.loop)
        self.reply_sink = reply_sink
        self.finish_hook = finish_hook
        self.npe = NounPhraseExtractor()
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

    def start(self, initial_message=None):
        """
        Call this so start the greeting state machine
        """
        if not initial_message:
            self.reply(choice(BasicResponses[self.state]))
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
        self.reply_sink(outgoing_message)

    def loop(self):
        while self.state != State.end:
            incoming_message = None
            try:
                incoming_message = self.message_queue.get(timeout=30)
                sleep(uniform(1, 3))
            except Empty:
                self.state = State.second_outreach if self.state == State.initial_outreach else State.give_up

            if self.state == State.free:
                #Create a custome state that handles free-form conversation
                res = self.sheldon.respond(incoming_message)
                if res:
                    break
            else:
                #Default FSM Pathway
                if self.state == State.end:
                    break
                outgoing_message = choice(BasicResponses[self.state])
                self.reply(outgoing_message)
                self.state = State(self.state + 2)
                if (self.state == State.inquiry2):
                    self.reply(choice(BasicResponses[self.state]))
                    self.state = State(self.state + 2)
                if (self.state == State.give_up):
                    break
        if self.finish_hook:
            self.finish_hook(self.conversation_partner)


def main():
    def reply_sink(message):
        print(message)

    def finish_hook(partner):
        print("finished convo", partner)

    gsm = ConversationStateMachine("", reply_sink, finish_hook, start_state=State.outreach_reply)
    def test():
        text = None
        text = input()
        gsm.start(text)
        while text != "":
            text = input()
            gsm.incoming_message(text)
    test()

if __name__ == "__main__":
    main()

from enum import Enum
from queue import Queue, Empty
from threading import Thread
from time import sleep
from random import uniform, choice
import re

from lang import NounPhraseExtractor

import wikipedia

class State(Enum):
    start = 1
    initial_outreach = 2
    second_outreach = 3
    outreach_reply = 4
    inquiry = 5
    inquiry_reply = 6
    inquiry2 = 7
    inquiry_reply2 = 8
    give_up = 9
    end = 10


class ConversationStateMachine:
    def __init__(self, partner_name, reply_sink, finish_hook=None, start_state=State.start):
        """
        Creates a greeting state machine that handles the greeting of a conversation by producing replies.
        :param partner_name: Name of the person we're conversing with
        :param reply_sink: Function to call with outgoing messages (irc privmsg probably)
        :param start_state: Can either be State.outreach_reply or State.start. State.start will initiate the conversation,
        while State.outreach_reply will partake in a conversation already initiated by someone else.
        """
        self.state = start_state
        self.conversation_partner = partner_name
        self.message_queue = Queue()
        self.thread = Thread(target=self.loop)
        self.reply_sink = reply_sink
        self.finish_hook = finish_hook
        self.npe = NounPhraseExtractor()

    def start(self, initial_message=None):
        """
        Call this so start the greeting state machine
        """
        self.begin_conversation(initial_message)
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
            handler = self.get_handler()
            outgoing_message = handler(incoming_message)
            self.reply(outgoing_message)
        if self.finish_hook:
            self.finish_hook(self.conversation_partner)

    def handle_give_up(self, message):
        assert self.state == State.give_up
        assert message is None
        self.state = State.end
        return "whatever"

    def begin_conversation(self, initial_message):
        if self.state == State.start:
            self.state = State.initial_outreach
            self.reply(self.perform_outreach())
        elif self.state == State.outreach_reply:
            self.reply(self.handle_outreach(initial_message))

    def perform_outreach(self):
        if self.state == State.second_outreach:
            reply = "are you there??"
        else:
            reply = "hello there"
        self.state = State.inquiry
        return reply

    def perform_inquiry(self, outreach_reply):
        self.state = State.inquiry_reply2
        return "generic inquiry"

    def handle_inquiry(self, inquiry):
        nps = self.npe.get_noun_phrases(inquiry)
        reply = None
        if len(nps) > 0:
            # create a reply using extracted noun phrases
            reply = self.create_reply(nps)

        if not reply:
            # they didn't say anything interesting
            # i.e. we could not extract any named entities or noun phrases
            if self.state == State.inquiry_reply2:
                reply = "default_inquiry_reply"
            else:
                reply = "default_inquiry_reply + default_inquiry2"
        self.state = State.end
        return reply

    def handle_outreach(self, outreach):
        self.state = State.inquiry_reply
        return "outreach reply"

    def get_handler(self):
        return {
            State.initial_outreach: self.perform_outreach,
            State.second_outreach: self.perform_outreach,
            State.inquiry: self.perform_inquiry,
            State.inquiry_reply: self.handle_inquiry,
            State.inquiry2: self.perform_inquiry,
            State.inquiry_reply2: self.handle_inquiry,
            State.give_up: self.handle_give_up
        }[self.state]

    def create_reply(self, entities):
        # fetch summaries of named entities if they exist
        wiki_summaries = []
        for ent in entities:
            try:
                summary = wikipedia.summary(ent)
                wiki_summaries.append(summary)
            except:
                # an exception is thrown when the search fails
                pass
        wiki_summaries = [re.sub(r"\s\(.*\),?", "", s) for s in wiki_summaries]
        return "Did you know that " + wiki_summaries[0] if len(wiki_summaries) > 0 else None

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
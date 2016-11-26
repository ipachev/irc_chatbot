from enum import Enum
from queue import Queue, Empty
from threading import Thread


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


class GreetingStateMachine:

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

    def start(self):
        """
        Call this so start the greeting state machine
        """
        self.begin_conversation()
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
        self.reply_sink("{}: {}".format(self.conversation_partner, message))

    def loop(self):
        while self.state != State.end:
            incoming_message = None
            try:
                incoming_message = self.message_queue.get(timeout=30)
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

    def begin_conversation(self):
        if self.state == State.start:
            self.state = State.initial_outreach
            self.reply(self.perform_outreach())
        elif self.state == State.outreach_reply:
            self.reply(self.handle_outreach())

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
        if self.state == State.inquiry_reply2:
            reply = "inquiry_reply2"
        else:
            reply = "inquiry_reply + inquiry2"
        self.state = State.end
        return reply

    def handle_outreach(self):
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

def reply_sink(message):
    print(message)

def finish_hook(partner):
    print("finished convo with", partner)



def main():
    gsm = GreetingStateMachine("test_partner", reply_sink, finish_hook, start_state=State.outreach_reply)
    def test():
        text = None
        text = input()
        gsm.incoming_message(text)
        gsm.start()
        while text != "":
            text = input()
            gsm.incoming_message(text)
    test()


if __name__ == "__main__":
    main()
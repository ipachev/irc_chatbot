from enum import IntEnum
from random import choice

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
    abruptend = 10
    give_up = 11
    free = 12
    end = 13


BasicResponses = {State.initial_outreach: ["hi, I do hope you will have something interesting to say.", "Hello, my talents are abundant in the sciences but somewhat lacking in social customs - you have been warned."],
    State.second_outreach: ["My time is considerably more precious than yours, please respect it.", "I could have reread all of Knuth in the time it is taking you to respond."],
    State.outreach_reply: ["hi, I do hope you will have something interesting to say.", "I'm already bored with this conversation"],
    State.inquiry: ["I already know what you are going to say, but how are you?", "Social customs obligate me to ask how are you doing?"],
    State.inquiry_reply: ["I'm experiencing high-levels of dopamine right now!", "I would be better if there were some people capable of intelligent conversation."],
    State.absorb: None,
    State.inquiry2: ["how about you?", "and yourself?"],
    State.inquiry_reply2: ["I'll be better when the pleasantries are over.", "I’m fine, thanks for asking.  Now let's talk about something meaningful."],
    State.abruptend: ["Have we at this point met our social obligations?"],
    State.give_up: ["Ok, forget you.", "Whatever.", "I didn't want to talk to you anyway."]
}

class Generic:
    def __init__(self, reply):
        self.reply = reply
        self.state = State.outreach_reply

    def initiate(self):
        self.reply(choice(BasicResponses[State.initial_outreach]))
        self.state = State.inquiry

    def handle_timeout(self):
        self.state = State.second_outreach if self.state == State.inquiry else State.give_up

    def handle_message(self, msg):
        if self.state == State.second_outreach and msg:
            self.state = State.inquiry

        if self.state != State.absorb:
            outgoing_message = choice(BasicResponses[self.state])
            self.reply(outgoing_message)

        if self.state == State.give_up or self.state == State.end:
            return True
        elif self.state == State.inquiry_reply2:
            self.state = State.free
        elif self.state == State.inquiry_reply:
            self.reply(choice(BasicResponses[State.inquiry2]))
            self.state = State(self.state + 4)
        else:
            self.state = State(self.state + 2)
        return False

    def delegate(self, msg):
        return self.state == State.free

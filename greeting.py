from enum import Enum
from time import time

class GreetingStateMachine:

    def __init__(self):
        self.state = State.start
        self.timeout = 30

    def wait_reply(self, ...):
        expected_state = GreetingStateMachine.successor_state(self.state)
        # todo: write some code here and wait for timeout and stuff

    @staticmethod
    def successor_state(state):
        return {
            State.start : State.initial_outreach,
            State.initial_outreach : State.outreach_reply,
            State.second_outreach : State.outreach_reply,
            State.outreach_reply : State.inquiry,
            State.inquiry : State.inquiry_reply,
            State.inquery_reply : State.inquery2,
            State.inquery2 : State.inquiry_reply2,
            State.inquiry_reply2 : State.end,
            State.give_up : State.end
        }[state]


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
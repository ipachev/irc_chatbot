from conversation import ConversationStateMachine, State

class Monitor:
    def __init__(self, send_message):
        self.conversations = {}
        self.send_message = send_message

    def handle_indirect(self, nick, cmd):
        print("YOU TALKING TO ME?")

    def handle_direct(self, nick, cmd):
        if nick not in self.conversations and (cmd == "hello" or cmd == "hi"):
            self.join_conversation(nick, cmd)
        elif nick in self.conversations:
            self.conversations[nick].incoming_message(cmd)
        else:
            self.send_message(nick + ": Conventional manners dictate that you initiate conversations with a proper greeting.")

    def join_conversation(self, partner_name, initial_message=None):
        if partner_name not in self.conversations:
            print("Joined conversation with", partner_name)
            new_convo = ConversationStateMachine(partner_name, self.send_message, self.finish_conversation, State.outreach_reply)
            self.conversations[partner_name] = new_convo
            new_convo.start(initial_message)
            return new_convo

    def start_conversation(self, partner_name):
        if partner_name not in self.conversations:
            print("Started conversation with", partner_name)
            new_convo = ConversationStateMachine(partner_name, self.send_message, self.finish_conversation, State.start)
            self.monitor.conversations[partner_name] = new_convo
            new_convo.start()
            return new_convo

    def finish_conversation(self, partner_name):
        print("Removed conversation with", partner_name)
        del self.conversations[partner_name]

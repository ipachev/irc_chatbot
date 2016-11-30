from random import randint
import time
from conversation import ConversationStateMachine
from lang import NounPhraseExtractor

class Monitor:
    def __init__(self, send_message):
        self.conversations = {}
        self.send_message = send_message
        self.npe = NounPhraseExtractor()
        self.lastinitiate = time.time()

    def quit(self):
        for nick in self.conversations:
            self.conversations[nick].stop()

    def handle_indirect(self, nick, cmd):
        now = time.time()
        if now - self.lastinitiate < 3:
            self.lastinitiate = now
            return
        elif nick in self.conversations:
            return
        if (randint(1, 100) > 98 or "lonely" in cmd):
            self.start_conversation(nick)
        else:
            try:
                entities = self.npe.get_noun_phrases(cmd)
                options = [self.npe.get_sentence(entity) for entity in entities]
                for opt in options:
                    if len(opt):
                        self.join_conversation(nick, cmd, "sheldon")
                        return
            except:
                return

    def handle_direct(self, nick, cmd):
        if nick not in self.conversations and (cmd == "hello" or cmd == "hi"):
            self.join_conversation(nick, cmd)
        elif nick in self.conversations:
            self.conversations[nick].incoming_message(cmd)
        else:
            self.send_message(nick + ": Conventional manners dictate that you initiate conversations with a proper greeting.")

    def join_conversation(self, partner_name, initial_message=None, default_persona="generic"):
        if partner_name not in self.conversations:
            print("Joined conversation with", partner_name)
            new_convo = ConversationStateMachine(partner_name, self.send_message, self.finish_conversation, default_persona)
            self.conversations[partner_name] = new_convo
            new_convo.start(initial_message)
            return new_convo

    def start_conversation(self, partner_name):
        if partner_name not in self.conversations:
            print("Started conversation with", partner_name)
            new_convo = ConversationStateMachine(partner_name, self.send_message, self.finish_conversation)
            self.conversations[partner_name] = new_convo
            new_convo.start()
            return new_convo

    def finish_conversation(self, partner_name):
        print("Removed conversation with", partner_name)
        del self.conversations[partner_name]

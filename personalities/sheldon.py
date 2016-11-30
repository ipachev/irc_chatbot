from random import choice
import re
import nltk.data

from lang import NounPhraseExtractor

flattery = [
"You're talking to one of the three men in the Western Hemisphere capable of following that train of thought.",
"I'm a physicist. I have a working knowledge of the entire universe and everything it contains.",
"I'm exceedingly smart. I graduated college at fourteen. While my brother was getting an STD, I was getting a Ph.D. Penicillin can't take this away.",
"I am a grown man. I am a professional scientist. And I currently occupy the moral high ground."
]

defenses = [
"Yes, well, I'm polymerized tree sap and you're an inorganic adhesive, so whatever verbal projectile you launch in my direction is reflected off of me, returns on its original trajectory and adheres to you.",
"You hypocrite!",
"That is demonstrably fallacious.",
"I cry because others are stupid, and that makes me sad.",
"Sometimes your lack of social skills astonishes me.",
"I must say, I am shocked by this betrayal.",
"That's not true, my mother had me tested.",
"You mess with the bull, you get the horns.",
"That's axiomatically wrong."
]

negativewords = ["ignorant", "oblivious", "uncouth", "annoying", "annoy", "rude", "inappropriate", "frustrate", "obscene", "know-it-all", "loud", "bad", "frustrating", "stupid", "lame"]

class Sheldon:
    def __init__(self, reply):
        self.npe = NounPhraseExtractor()
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.reply = reply
        self.nxtmessage = None
        self.lastinsight = None

    def handle_timeout(self):
        self.nxtmessage = "It must be terribly inconvenient to be such a slow thinker; I'm done talking to you."

    def delegate(self, msg):
        return False

    def handle_message(self, inquiry):
        reply = None
        if self.nxtmessage:
            self.reply(self.nxtmessage)
            return True

        try:
            nps = self.npe.get_noun_phrases(inquiry)
        except:
            nps = []


        if len(nps) > 0:
            kind = "question" if "?" in inquiry else "statement"
            reply = self.__create_reply(nps, kind=kind)
        elif any([w in inquiry for w in negativewords]):
            reply = choice(defenses)
        elif self.lastinsight:
            try:
                nps = self.npe.get_noun_phrases(self.lastinsight)
                kind = "question" if "?" in inquiry else "statement"
                reply = self.__create_reply(nps, kind=kind)
            except:
                pass
        if not reply:
            kind = "question" if "?" in inquiry else "statement"
            self.reply(choice(flattery))
            reply = "At least come up with an intelligent " + kind + "."
        self.reply(reply)
        return False

    def __create_reply(self, entities, kind):
        options = [self.npe.get_sentence(entity) for entity in entities]
        for opt in options:
            if len(opt) > 0:
                fact = choice(opt)
                fact = fact[0].lower() + fact[1:]
                if (fact == self.lastinsight):
                    continue
                if self.lastinsight:
                    self.lastinsight = None
                    return "Additionally, it is true that " + fact

                self.lastinsight = fact
                if kind == "question":
                    return "You suprise me by your ignorance; it is obvious that " + fact
                else:
                    return "Did you know that " + fact[:-1] + "?"
        return None


class Sheldon:
    def __init__(self):
        pass

    def respond(self, msg):
        return False

    def handle_inquiry(self, inquiry):
        nps = self.npe.get_noun_phrases(inquiry)
        reply = None
        kind = "question" if "?" in inquiry else "statement"
        if len(nps) > 0:
            # create a reply using extracted noun phrases
            reply = self.create_reply(nps, kind=kind)

        if not reply:
            # they didn't say anything interesting
            # i.e. we could not extract any named entities or noun phrases
            if self.state == State.inquiry_reply2:
                reply = "I'm not sure how to respond to that, but "
            else:
                reply = "default_inquiry_reply + default_inquiry2"
        self.state = State.end
        return reply

    def create_reply(self, entities, kind):
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

        if len(wiki_summaries) > 0:
            summary = self.sent_detector.tokenize(wiki_summaries[0])[0]
            if kind == "question":
                return "You suprise me by your ignorance; it is obvious that " + summary
            else:
                return "Did you know that " + summary + "?"
        return None

from irc import Channel
from bot import Bot

ch = Channel("chat.freenode.net", "#CPE582")
bot = Bot("ivan_test")
bot.connect(ch)
ch.run()
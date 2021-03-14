import osu_irc

class BanchoPoster(osu_irc.Client):
    channel = None
    pm = False

    @classmethod
    def configure(cls, channel, pm=False):
        cls.channel = channel
        cls.pm = pm

    def prepare(self, content):
        self.content = content

    async def onReady(self):
        await getattr(self, 'sendPM' if self.pm else 'sendMessage')(self.channel, self.content)
        self.stop()


import config
import sys
BanchoPoster.configure(config.irc_channel, config.pm)
bot = BanchoPoster(nickname=sys.argv[1], token=sys.argv[2])
bot.prepare(sys.argv[3])
bot.run()

import logging
import time
import osu_irc

class BanchoPoster(osu_irc.Client):
    channel : str = None
    pm = False

    @classmethod
    def configure(cls, channel, pm=False):
        cls.channel = channel
        cls.pm = pm

    def prepare(self, content):
        self.content = content

    async def onReady(self):
        await self.joinChannel(self.channel)
        time.sleep(1)
        func = getattr(self, 'sendPM' if self.pm else 'sendMessage')
        await func(self.channel, self.content)
        time.sleep(5)
        self.stop()


import config
import sys
logging.basicConfig(level=logging.DEBUG)
BanchoPoster.configure(config.irc_channel, config.pm)
bot = BanchoPoster(nickname=sys.argv[1], token=sys.argv[2])
bot.prepare(sys.argv[3])
with open('debug-poster.txt', 'w') as f:
    f.write(str(sys.argv))
    f.write(str(config.__dir__()))
    f.write(str(bot))
bot.run()

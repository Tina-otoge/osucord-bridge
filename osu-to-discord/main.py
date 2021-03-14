import logging
import requests
import json
import osu_irc
from bs4 import BeautifulSoup

class MessagePoster:
    OSU_PROFILE_URL = 'https://osu.ppy.sh/users'

    def __init__(self, webhook_url):
        self._webhook_url = webhook_url

    def post(self, message: osu_irc.Message):
        try:
            user_page = requests.get(f'{self.OSU_PROFILE_URL}/{message.user_name}')
            soup = BeautifulSoup(user_page.content, 'html.parser')
            data = json.loads(soup.find(id='json-user').contents[0])
            avatar_url = data.get('avatar_url')
        except Exception as e:
            logging.warning(e, exc_info=True)
            avatar_url = 'https://osu.ppy.sh/images/layout/avatar-guest.png'
        resp = requests.post(
            self._webhook_url,
            data={
                'content': message.content,
                'username': message.user_name,
                'avatar_url': avatar_url,
            }
        )
        logging.debug('Sent request to Discord, got {resp}', resp=resp)

class BanchoListener(osu_irc.Client):
    def attach_poster(self, poster):
        self.poster = poster

    def watch(self, channel: str):
        self.channel = channel

    async def onReady(self):
        await self.joinChannel(self.channel)
        logging.debug('Joined channel {name}', name=self.channel)
        logging.debug('IRC bot ready')

    async def onMessage(self, message):
        self.poster.post(message)

if __name__ == '__main__':
    try:
        import config

        bot = BanchoListener(token=config.irc_password, nickname=config.username)
        poster = MessagePoster(config.webhook)
        bot.attach_poster(poster)
        bot.watch(config.channel)
        bot.run()
    except (AttributeError, ModuleNotFoundError):
        print('Invalid or not found config.py file')

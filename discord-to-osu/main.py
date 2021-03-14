import json
import logging
import subprocess
import discord
import pathlib


class Data:
    def __init__(self, path='./data.json'):
        self.path = path
        try:
            with open(self.path) as f:
                self._data = json.load(f)
        except FileNotFoundError:
            self._data = {}

    def get(self, key, fallback=None):
        return self._data.get(key, fallback)

    def set(self, key, value, save=True):
        self._data[key] = value
        if save:
            self.save()

    def save(self):
        with open(self.path, 'w') as f:
            json.dump(self._data, f, indent=2)


class DiscordListener(discord.Client):
    def watch(self, channel):
        self.channel = channel

    async def handle_register(self, message: discord.Message):
        words = message.content.split()
        try:
            self.data.set(message.author.id, {'nickname': words[1], 'token': words[2]})
            await message.channel.send('Registered!')
        except:
            await message.channel.send('Invalid parameters, you need to provide your osu! nickname followed by your IRC token')

    def forward(self, message: discord.Message, creds: dict):
        process = subprocess.Popen([
            'python',
            self.poster_path,
            creds['nickname'], creds['token'],
            message.content,
        ])
        logging.debug(process)
        return True

    async def on_ready(self):
        self.poster_path = (pathlib.Path(__file__).parent / 'poster.py').absolute()
        self.data = Data()
        logging.debug(f'Discord bot {self.user} ready')

    async def on_message(self, message: discord.Message):
        if message.author == self.user or message.author.bot:
            return
        if message.content.startswith('!osuirc'):
            return await self.handle_register(message)
        if str(message.channel.id) != self.channel:
            return
        creds = self.data.get(str(message.author.id))
        if not creds or not creds.get('nickname') or not creds.get('token'):
            return
        logging.info('Fowarding message to osu!')
        self.forward(message, creds)


import config

logging.basicConfig(level=logging.DEBUG)
bot = DiscordListener()
bot.watch(config.channel)
bot.run(config.token)

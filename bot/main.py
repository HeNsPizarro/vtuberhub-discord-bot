# entry point del bot
import discord
from discord import app_commands
from aiohttp import web

from bot.config import DISCORD_TOKEN
from bot.commands.vtuber import VTuberGroup
from bot.webhook_server import create_webhook_app


class VTuberBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.add_command(VTuberGroup())
        await self.tree.sync()

        app = create_webhook_app(self)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 8080)
        await site.start()

        print("🌐 Webhook server escuchando en :8080")

    async def on_ready(self):
        print(f"🤖 Bot conectado como {self.user}")


bot = VTuberBot()
bot.run(DISCORD_TOKEN)


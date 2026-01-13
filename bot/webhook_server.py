import discord
from aiohttp import web

from bot.services.vtuber_service import VTuberService
from bot.utils.embeds import vtuber_live_embed


def create_webhook_app(bot: discord.Client):
    app = web.Application()

    async def vtuber_live(request):
        data = await request.json()
        # print(">>> WEBHOOK RECIBIDO:", data)

        vtuber_id = data.get("vtuber_id")
        nombre = data.get("nombre")
        live = data.get("live", False)

        if not vtuber_id or not nombre:
            return web.json_response(
                {"error": "vtuber_id y nombre requeridos"},
                status=400
            )

        # 🔔 Solo notificamos si está EN VIVO
        if not live:
            return web.json_response({"status": "ok", "info": "offline"})

        # 1️⃣ Obtener followers (por ID, no por nombre)
        followers = VTuberService.get_followers(vtuber_id)
        if not followers:
            return web.json_response({"status": "ok", "info": "sin followers"})

        # 2️⃣ Armar embed
        embed = vtuber_live_embed(data)

        # 3️⃣ Enviar por server
        for guild in bot.guilds:
            channel_id = VTuberService.get_notify_channel(guild.id)
            if not channel_id:
                continue

            channel = guild.get_channel(channel_id)
            if not channel:
                continue

            # usuarios del server
            guild_user_ids = {member.id for member in guild.members}

            # followers que están en este server
            mentioned_users = [
                uid for uid in followers
                if uid in guild_user_ids
            ]

            if not mentioned_users:
                continue

            mentions = " ".join(f"<@{uid}>" for uid in mentioned_users)

            await channel.send(
                content=mentions,
                embed=embed
            )

        return web.json_response({"status": "ok"})

    # 🔗 ÚNICO endpoint necesario
    app.router.add_post("/vtuber/live", vtuber_live)

    return app

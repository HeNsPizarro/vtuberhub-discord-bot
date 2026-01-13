 # /vtuber buscar, links, imagen, etc

import discord
from discord import app_commands

from bot.services.vtuber_service import VTuberService
from bot.utils.embeds import vtuber_embed
from bot.utils.views import VTuberLinksView
from bot.utils.views import VTuberOnlineView
from bot.services.vtuber_service import VTuberService
from bot.database.follows import follow_vtuber
from bot.database.follows import unfollow_vtuber
from bot.database.follows import get_followed_vtubers
from bot.services.vtuber_service import VTuberService
from bot.utils.embeds import vtuber_follows_embed


class VTuberGroup(app_commands.Group):
    def __init__(self):
        super().__init__(
            name="vtuber",
            description="Comandos relacionados a VTubers"
        )

    @app_commands.command(
        name="buscar",
        description="Buscar información de una VTuber"
    )
    @app_commands.describe(login="Login de la VTuber en Twitch")
    async def buscar(self, interaction: discord.Interaction, login: str):
        # 1️⃣ Buscar VTuber (n8n / DB)
        data = VTuberService.buscar_vtuber(login)

        if not data:
            await interaction.response.send_message(
                f"❌ No se encontró la VTuber **{login}**",
                ephemeral=True
            )
            return

        user_id = interaction.user.id
        vtuber_id = data.get("vtuber_id")

        # 2️⃣ Estado de seguimiento
        is_following = False
        if vtuber_id:
            is_following = VTuberService.user_follows_vtuber(
                user_id=user_id,
                vtuber_id=vtuber_id
            )

        data["is_following"] = is_following

        # 3️⃣ Estado del stream
        stream_status = None
        if vtuber_id:
            stream_status = VTuberService.get_stream_status(vtuber_id)

        data["stream_status"] = stream_status

        # 4️⃣ URL de plataforma (Twitch por ahora)
        stream_url = None
        if data.get("platform") == "twitch" and data.get("login_name"):
            stream_url = f"https://www.twitch.tv/{data['login_name']}"

        # 5️⃣ Embed
        embed = vtuber_embed(data)

        # 6️⃣ View de detalle (follow / plataforma / más info)
        from bot.utils.views import VTuberDetailView

        view = VTuberDetailView(
            user_id=user_id,
            vtuber_data=data,
            stream_url=stream_url
        )

        # 7️⃣ Respuesta
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True
        )


    @app_commands.command(
        name="links",
        description="Mostrar links oficiales de una VTuber"
    )
    @app_commands.describe(nombre="Nombre de la VTuber")
    async def links(self, interaction: discord.Interaction, nombre: str):
        data = VTuberService.obtener_links(nombre)

        if not data:
            await interaction.response.send_message(
                f"❌ No se encontraron links para **{nombre}**",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title=f"🔗 Links de {data['nombre']}",
            color=discord.Color.purple()
        )

        if data.get("youtube"):
            embed.add_field(name="📺 YouTube", value=data["youtube"], inline=False)
        if data.get("twitch"):
            embed.add_field(name="🎮 Twitch", value=data["twitch"], inline=False)
        if data.get("twitter"):
            embed.add_field(name="🐦 Twitter/X", value=data["twitter"], inline=False)

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    @app_commands.command(
        name="online",
        description="Mostrar VTubers que están en vivo"
    )
    async def online(self, interaction: discord.Interaction):
        vtubers = VTuberService.obtener_vtubers_online()

        # 🔥 ORDENAR POR VIEWERS (mayor a menor)
        vtubers.sort(
            key=lambda v: v.get("viewers", 0),
        reverse=True
        )

        if not vtubers:
            await interaction.response.send_message(
            "😴 No hay VTubers en vivo ahora mismo.",
            ephemeral=True
            )
            return
        
        from bot.utils.views import build_base_embed
        embed = build_base_embed("all", len(vtubers))
        embed.set_footer(text="VTuberInfoBot • estado en tiempo real")

        view = VTuberOnlineView(vtubers)
        view.base_embed = embed

        await interaction.response.send_message(
            embed=embed,
            view=view,
            #ephemeral=True
        )

    @app_commands.command(
        name="follow",
        description="Seguir una VTuber"
    )
    @app_commands.describe(login="Login de la VTuber en Twitch")
    async def follow(self, interaction: discord.Interaction, login: str):
        await interaction.response.defer(ephemeral=True)

        data = VTuberService.buscar_vtuber(login)
        if not data:
            await interaction.followup.send(
                f"❌ No se encontró la VTuber **{login}**"
            )
            return

        vtuber_id = data.get("vtuber_id")
        if not vtuber_id:
            await interaction.followup.send(
                "⚠️ Error interno: VTuber sin ID"
            )
            return

        created = follow_vtuber(
            user_id=interaction.user.id,
            vtuber_id=vtuber_id
        )

        if created:
            await interaction.followup.send(
                f"⭐ Ahora seguís a **{data.get('display_name_text', login)}**"
            )
        else:
            await interaction.followup.send(
                f"ℹ️ Ya seguías a **{data.get('display_name_text', login)}**"
            )




    @app_commands.command(
        name="follows",
        description="Ver las VTubers que seguís"
    )
    async def follows(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        vtuber_ids = get_followed_vtubers(interaction.user.id)

        if not vtuber_ids:
            embed = vtuber_follows_embed(interaction.user, [])
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        vtubers = VTuberService.get_vtubers_by_ids(vtuber_ids)
        embed = vtuber_follows_embed(interaction.user, vtubers)

        await interaction.followup.send(embed=embed, ephemeral=True)



    @app_commands.command(
        name="setchannel",
        description="Configurar el canal de notificaciones de VTubers"
    )
    async def setchannel(self, interaction: discord.Interaction):
        if not interaction.guild:
            await interaction.response.send_message(
                "❌ Este comando solo se puede usar en servidores",
                ephemeral=True
            )
            return

        channel = interaction.channel

        VTuberService.set_notify_channel(
            interaction.guild.id,
            channel.id
        )

        await interaction.response.send_message(
            f"📣 Las notificaciones se enviarán en {channel.mention}",
            ephemeral=True
        )





    @app_commands.command(
        name="unfollow",
        description="Dejar de seguir una VTuber"

    )
    @app_commands.describe(login="Login de la VTuber en Twitch")
    async def unfollow(self, interaction: discord.Interaction, login: str):
        await interaction.response.defer(ephemeral=True)

        data = VTuberService.buscar_vtuber(login)
        if not data:
            await interaction.followup.send(
                f"❌ No se encontró la VTuber **{login}**"
            )
            return

        vtuber_id = data.get("vtuber_id")
        if not vtuber_id:
            await interaction.followup.send(
                "⚠️ Error interno: VTuber sin ID"
            )
            return

        deleted = unfollow_vtuber(
            user_id=interaction.user.id,
            vtuber_id=vtuber_id
        )

        if deleted:
            await interaction.followup.send(
                f"💔  Dejaste de seguir a **{data.get('display_name_text', login)}**"
            )
        else:
            await interaction.followup.send(
                f"ℹ️ No estabas siguiendo a **{data.get('display_name_text', login)}**"
            )

        
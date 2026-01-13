import discord
import math
from bot.utils.embeds import vtuber_live_embed
from bot.database.follows import get_followed_vtubers
from bot.services.vtuber_service import VTuberService
from bot.utils.embeds import vtuber_embed




PAGE_SIZE = 25  # límite real de Discord

class VTuberLinksView(discord.ui.View):
    def __init__(self, *, stream_url=None, youtube=None, twitch=None, twitter=None):
        super().__init__(timeout=None)

        if stream_url:
            self.add_item(
                discord.ui.Button(
                    label="▶️ Ver stream",
                    url=stream_url,
                    style=discord.ButtonStyle.link
                )
            )
        else:
            if youtube:
                self.add_item(
                    discord.ui.Button(
                        label="📺 YouTube",
                        url=youtube,
                        style=discord.ButtonStyle.link
                    )
                )

            if twitch:
                self.add_item(
                    discord.ui.Button(
                        label="🎮 Twitch",
                        url=twitch,
                        style=discord.ButtonStyle.link
                    )
                )

        if twitter:
            self.add_item(
                discord.ui.Button(
                    label="🐦 Twitter/X",
                    url=twitter,
                    style=discord.ButtonStyle.link
                )
            )


def build_base_embed(mode: str, count: int) -> discord.Embed:
    separator = "┗━━━━━━━━━━━━━━━━•(=^●ω●^=)•━━━━━━━━━━━━━━━━━┛" 

    if mode == "followed":
        title = "⭐ TUS VTUBERS FAVORITAS EN VIVO ⭐"
        description = (
            "┏━━━━━━━━━━━━━━━━━•(=^●ω●^=)•━━━━━━━━━━━━━━━━━┓\n\n"
            "Estas son las VTubers que seguís y que están transmitiendo.\n\n"
            "👇 Seleccioná una VTuber del menú para ver el stream 👇\n\n"
            f"{separator}"
        )
        color = discord.Color.gold()

    elif mode == "top":
        title = "🔥 TOP VTUBERS EN VIVO 🔥"
        description = (
            "┏━━━━━━━━━━━━━━━━━•(=^●ω●^=)•━━━━━━━━━━━━━━━━━┓\n\n"
            "Los streams con más viewers en este momento, Top 15 vtubers.\n\n"
            "👇  Seleccioná una VTuber del menú para ver el stream 👇\n\n"
            f"{separator}"
        )
        color = discord.Color.orange()

    else:  # all
        title = f"🔴 VTUBERS EN VIVO AHORA 🔴 ({count})"
        description = (
            "┏━━━━━━━━━━━━━━━━━•(=^●ω●^=)•━━━━━━━━━━━━━━━━━┓\n\n"
            "Estas son todas las VTubers que están transmitiendo ahora.\n\n"
            "👇 Seleccioná una VTuber del menú para ver el stream 👇\n\n"
            f"{separator}"
        )
        color = discord.Color.red()

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    embed.set_footer(text="VTuberInfoBot • estado en tiempo real")
    return embed



def viewer_prefix(viewers: int | None) -> str:
    if viewers is None:
        return "🔺"
    if viewers >= 6000:
        return "🔥"
    if viewers >= 1000:
        return "🔴"
    return "🔺"

class VTuberOnlineSelect(discord.ui.Select):
    def __init__(self, vtubers: list[dict], page: int):
        start = page * PAGE_SIZE
        end = start + PAGE_SIZE
        page_items = vtubers[start:end]

        options = [
            discord.SelectOption(
                label=f"{viewer_prefix(vt.get('viewers'))} {vt['nombre']}",
                description=vt.get("plataforma", "Twitch"),
                value=vt["nombre"]
            )
            for vt in page_items
        ]

        super().__init__(
            placeholder=f"🔴 Seleccioná una VTuber (pág. {page + 1})",
            min_values=1,
            max_values=1,
            options=options
        )

        self.vtubers_map = {vt["nombre"]: vt for vt in vtubers}

    async def callback(self, interaction: discord.Interaction):
        nombre = self.values[0]
        data = self.vtubers_map[nombre]

        embed = vtuber_live_embed(data)

        from bot.utils.views import VTuberDetailView

        await interaction.response.edit_message(
            embed=embed,
            view=VTuberDetailView(self.view)
        )


class PageButton(discord.ui.Button):
    def __init__(self, label: str, direction: int):
        super().__init__(label=label, style=discord.ButtonStyle.secondary)
        self.direction = direction

    async def callback(self, interaction: discord.Interaction):
        view: VTuberOnlineView = self.view
        view.page += self.direction

        view.clear_items()
        view.build()

        await interaction.response.edit_message(view=view)

class AllButton(discord.ui.Button):
    def __init__(self, active: bool):
        super().__init__(
            label="✅​ Todos",
            style=discord.ButtonStyle.primary if active else discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        view: VTuberOnlineView = self.view

        # Si ya estamos en 'all', no hacemos nada
        if view.mode == "all":
            await interaction.response.defer()
            return

        view.vtubers = view.all_vtubers
        view.mode = "all"
        view.page = 0
        view.total_pages = math.ceil(len(view.vtubers) / PAGE_SIZE)
        view.base_embed = build_base_embed(view.mode, len(view.vtubers))

        view.clear_items()
        view.build()

        await interaction.response.edit_message(
            embed=view.base_embed,
            view=view
        )

class FollowedButton(discord.ui.Button):
    def __init__(self, active: bool):
        super().__init__(
            label="⭐ Seguidos",
            style=discord.ButtonStyle.primary if active else discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        view: VTuberOnlineView = self.view

        from bot.services.vtuber_service import VTuberService
        from bot.utils.views import filter_followed

        # Si ya estamos en 'followed', no hacemos nada
        if view.mode == "followed":
            await interaction.response.defer()
            return

        followed_ids = get_followed_vtubers(interaction.user.id)

        if not followed_ids:
            await interaction.response.send_message(
                "😴 No seguís ninguna VTuber que esté en vivo ahora.",
            ephemeral=True
            )
            return
        
        filtered = [
            vt for vt in view.all_vtubers
            if vt.get("vtuber_id") in followed_ids
        ]

        if not filtered:
            await interaction.response.send_message(
                "😴 Ninguna VTuber que seguís está en vivo ahora mismo.",
                ephemeral=True
            )
            return

        view.vtubers = filtered
        view.mode = "followed"
        view.page = 0
        view.total_pages = math.ceil(len(view.vtubers) / PAGE_SIZE)
        view.base_embed= build_base_embed(view.mode, len(view.vtubers))

        view.clear_items()
        view.build()

        await interaction.response.edit_message(
            embed=view.base_embed,
            view=view
        )


class TopViewersButton(discord.ui.Button):
    def __init__(self, active: bool):
        super().__init__(
            label="🔥 Top viewers",
            style=discord.ButtonStyle.primary if active else discord.ButtonStyle.secondary
        )

    async def callback(self, interaction: discord.Interaction):
        view: VTuberOnlineView = self.view

        # Si ya estamos en 'top', no hacemos nada
        if view.mode == "top":
            await interaction.response.defer()
            return

        # Ordenar por viewers (mayor a menor)
        sorted_vtubers = sorted(
            view.all_vtubers,
            key=lambda v: v.get("viewers", 0),
            reverse=True
        )

        # (Opcional) limitar a top 15
        view.vtubers = sorted_vtubers[:15]
        view.mode = "top"
        view.page = 0
        view.total_pages = math.ceil(len(view.vtubers) / PAGE_SIZE)
        view.base_embed = build_base_embed(view.mode, len(view.vtubers))

        view.clear_items()
        view.build()

        await interaction.response.edit_message(
            embed=view.base_embed,
            view=view
        )


class VTuberOnlineView(discord.ui.View):
    def __init__(self, vtubers: list[dict]):
        super().__init__(timeout=120)
        self.all_vtubers = vtubers          # lista completa
        self.vtubers = vtubers              # lista activa
        self.mode = "all"                   # all | followed
        self.page = 0
        self.total_pages = math.ceil(len(self.vtubers) / PAGE_SIZE)
        self.build()

    def build(self):
        # Select
        self.add_item(VTuberOnlineSelect(self.vtubers, self.page))
         
        # Botones de modo (exclusivos)
        self.add_item(AllButton(active=self.mode == "all"))
        self.add_item(TopViewersButton(active=self.mode == "top"))
        self.add_item(FollowedButton(active=self.mode == "followed"))


        # Botones de paginación
        if self.total_pages > 1:
            if self.page > 0:
                self.add_item(PageButton("⬅️ Anterior", -1))

            if self.page < self.total_pages - 1:
                self.add_item(PageButton("Siguiente ➡️", 1))


class BackToListButton(discord.ui.Button):
    def __init__(self, parent_view: "VTuberOnlineView"):
        super().__init__(
            label="⬅️ Volver a la lista",
            style=discord.ButtonStyle.secondary
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        
        self.parent_view.clear_items()
        self.parent_view.build()

        await interaction.response.edit_message(
            embed=self.parent_view.base_embed,
            view=self.parent_view
        )


class VTuberDetailView(discord.ui.View):
    def __init__(self, *, user_id: int, vtuber_data: dict, stream_url: str | None):
        super().__init__(timeout=None)

        self.user_id = user_id
        self.vtuber_data = vtuber_data
        self.stream_url = stream_url

        self.build()


    def build(self):
        self.clear_items()

        # 1️⃣ Botón de seguimiento (acción principal)
        if self.vtuber_data.get("is_following"):
            self.add_item(UnfollowButton(self))
        else:
            self.add_item(FollowButton(self))

        # 2️⃣ Botón de plataforma (dinámico)
        if self.stream_url:
            self.add_item(
                discord.ui.Button(
                    label="🟣 Twitch",
                    url=self.stream_url,
                    style=discord.ButtonStyle.link
                )
            )

        # 3️⃣ Botón Más info (Wiki)
        name = self.vtuber_data.get("display_name_text") or self.vtuber_data.get("login_name")
        wiki_url = f"https://virtualyoutuber.fandom.com/wiki/{name}"

        self.add_item(
            discord.ui.Button(
                label="📘 Más info",
                url=wiki_url,
                style=discord.ButtonStyle.link
            )
        )


    async def refresh(self, interaction: discord.Interaction):
        """Reconstruye embed + botones sin mandar mensaje nuevo"""
        new_embed = vtuber_embed(self.vtuber_data)
        self.build()

        await interaction.response.edit_message(
            embed=new_embed,
            view=self
        )

    # ======================================================
    # flitros
    # ======================================================

def filter_followed(vtubers: list[dict], followed_ids: list[int]) -> list[dict]:
    followed_set = set(followed_ids)

    return [
        vt for vt in vtubers
        if vt.get("vtuber_id") in followed_set
    ]


class VTuberFollowView(discord.ui.View):
    def __init__(self, *, user_id: int, vtuber_data: dict):
        super().__init__(timeout=None)
        self.user_id = user_id
        self.vtuber_data = vtuber_data

        is_following = vtuber_data.get("is_following", False)

        if is_following:
            self.add_item(UnfollowButton(self))
        else:
            self.add_item(FollowButton(self))



class FollowButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(
            label="Follow",
            emoji="⭐",
            style=discord.ButtonStyle.primary
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message(
                "❌ Este botón no es para vos.",
                ephemeral=True
            )
            return

        VTuberService.follow_vtuber(
            user_id=self.parent_view.user_id,
            vtuber_id=self.parent_view.vtuber_data["vtuber_id"]
        )

        self.parent_view.vtuber_data["is_following"] = True
        await self.parent_view.refresh(interaction)


class UnfollowButton(discord.ui.Button):
    def __init__(self, parent_view):
        super().__init__(
            label="Unfollow",
            emoji="💔",
            style=discord.ButtonStyle.secondary
        )
        self.parent_view = parent_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.parent_view.user_id:
            await interaction.response.send_message(
                "❌ Este botón no es para vos.",
                ephemeral=True
            )
            return

        VTuberService.unfollow_vtuber(
            user_id=self.parent_view.user_id,
            vtuber_id=self.parent_view.vtuber_data["vtuber_id"]
        )

        self.parent_view.vtuber_data["is_following"] = False
        await self.parent_view.refresh(interaction)
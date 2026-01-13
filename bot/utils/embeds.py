# helpers para embeds
import discord

TWITCH_COLOR = discord.Color.purple()
LANGUAGE_MAP = {
    "en": ("🇺🇸", "English"),
    "es": ("🇪🇸", "Español"),
    "ja": ("🇯🇵", "日本語"),
    "pt": ("🇧🇷", "Português"),
    "fr": ("🇫🇷", "Français"),
    "de": ("🇩🇪", "Deutsch"),
    "ko": ("🇰🇷", "한국어"),
    "ru": ("🇷🇺", "Русский"),
}

AGENCY_COLORS = {
    "vshojo": discord.Color.purple(),
    "hololive": discord.Color.blue(),
    "nijisanji": discord.Color.green(),
    "independiente": discord.Color.dark_gray(),
}







def format_language(lang: str | None) -> str:
    if not lang:
        return "❌ Desconocido"

    lang = lang.lower()
    flag, name = LANGUAGE_MAP.get(lang, ("🌐", lang.upper()))
    return f"{flag} {name}"

def vtuber_embed(data: dict) -> discord.Embed:
    display_name = (
        data.get("display_name_text")
        or data.get("login_name")
        or "VTuber"
    )

    base_description = data.get("description") or "Sin descripción disponible"

    # Limitar descripción (UX)
    if len(base_description) > 200:
        base_description = base_description[:297] + "…"

    platform = data.get("platform", "desconocida").capitalize()
    status = data.get("stream_status")

    embed = discord.Embed(
        color=discord.Color.purple()
    )

    # ─── Header / Identidad ──────────────────────────────
    embed.set_author(
        name=display_name,
        icon_url=data.get("avatar_url")
    )

    if data.get("avatar_url"):
        embed.set_thumbnail(url=data["avatar_url"])

    # ─── Estado del stream (máxima prioridad visual) ─────
    if status and int(status.get("is_live", 0)) == 1:
        embed.title = "🔴 En vivo ahora"
        embed.description = (
            f"🎮**{status.get('category', 'Sin categoría')}**\n"
            f"👥 Viewers {status.get('viewer_count', 0)} \n\n"
            f"{base_description}\n"
        )
    else:
        embed.title = "⚫ Offline por ahora\n\n"
        embed.description = base_description

    # ─── Info seguidos o no ─────────────────────────────────

    is_following = data.get("is_following", False)

    embed.add_field(
        name="⭐ Seguimiento",
        value = "✅ Seguida" if is_following else "❌ No la seguís",
        inline=True
    )

    # ─── Info secundaria ─────────────────────────────────
    platform_name = platform.lower()

    platform_emoji = {
        "twitch": "🟣",
        "youtube": "🔴",
        "kick": "🟢"
    }.get(platform_name, "📺")

    embed.add_field(
        name="📺 Plataforma",
        value=f"{platform_emoji} {platform}",
        inline=True
    )

    embed.add_field(
        name="🌐 Idioma",
        value=format_language(data.get("language")),
        inline=True
    )

    # ─── Footer / Branding ───────────────────────────────
    embed.set_footer(
        text="VTuberInfoBot • ficha del canal"
    )

    return embed


# ================================
# EMBED DE LIVE (NO TOCADO AÚN)
# ================================

def vtuber_live_embed(data: dict) -> discord.Embed:
    nombre = data["nombre"]
    plataforma = data.get("plataforma", "Twitch")
    stream_url = data["stream_url"]

    title = data.get("title", "En vivo ahora")
    game = data.get("game", "Desconocido")
    viewers = data.get("viewers")
    thumbnail = data.get("thumbnail_url")
    avatar = data.get("avatar_url")
    started_at = data.get("started_at")

    embed = discord.Embed(
        title=title,
        url=stream_url,
        color=TWITCH_COLOR
    )

    embed.set_author(
        name=f"🔴 {nombre} está en vivo en {plataforma}",
        icon_url=avatar,
        url=stream_url
    )

    if thumbnail:
        embed.set_image(url=f"{thumbnail}?t=live")

    embed.add_field(
        name="🎮 Playing",
        value=game,
        inline=True
    )

    if viewers is not None:
        embed.add_field(
            name="👀 Viewers",
            value=str(viewers),
            inline=True
        )

    embed.set_footer(
        text="VTuberInfoBot • El stream inició"
    )

    if started_at:
        try:
            embed.timestamp = discord.utils.parse_time(started_at)
        except Exception:
            pass

    return embed




def vtuber_follows_embed(user: discord.User, vtubers: list[dict]) -> discord.Embed:
    embed = discord.Embed(
        title="💙 TUS VTUBERS SEGUIDAS 💙",
        color=discord.Color.blue()
    )

    if not vtubers:
        embed.description = (
            "Todavía no seguís ninguna VTuber.\n\n"
            "Usá `/vtuber follow` para empezar ⭐"
        )
    else:
        embed.description = (
            "Las notificaciones con mención serán\n"
            "solo para las VTubers de esta lista.\n\n"
            "┏━━━━━━━━━•(=^●ω●^=)•━━━━━━━━━┓\n\n"
            + "\n".join(
                f"• **{vt.get('display_name_text', vt.get('login_name'))}**"
                for vt in vtubers
            )
            + "\n\n┗━━━━━━━━━•(=^●ω●^=)•━━━━━━━━━┛"
        )

    embed.set_author(
        name=f"🩵 {user.display_name} — VTuber Follows",
        icon_url=user.display_avatar.url
    )

    embed.set_footer(text="VTuberInfoBot • lista personal")
    return embed
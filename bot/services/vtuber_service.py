# lógica de negocio relacionada a VTubers
# BOT = cliente
# n8n = backend / DB / APIs

from bot.database.db import get_connection
from bot.services.n8n_client import (
    buscar_vtuber as buscar_en_n8n,
    obtener_vtubers_online as online_from_n8n
)

# ⚠️ IMPORTANTE
# Este service:
# - NO escribe VTubers en DB
# - NO consulta DB de VTubers
# - SOLO consume n8n
#
# La DB local queda reservada para:
# - follows
# - config de servidores
# (eso lo dejamos para el próximo paso)


class VTuberService:

    # ======================================================
    # VTUBERS (READ ONLY – n8n es la fuente de verdad)
    # ======================================================

    @staticmethod
    def buscar_vtuber(nombre: str) -> dict | None:
        """
        Busca una VTuber.
        El bot NO decide si existe o no:
        - n8n consulta DB
        - n8n consulta Twitch si hace falta
        - n8n guarda si corresponde
        - n8n devuelve el payload final
        """
        if not nombre:
            return None

        return buscar_en_n8n(nombre.lower())


    @staticmethod
    def obtener_vtubers_online() -> list[dict]:
        """
        VTubers online en tiempo real.
        No usa DB local.
        """
        return online_from_n8n()


    # ======================================================
    # PLACEHOLDERS (SE MIGRAN DESPUÉS)
    # ======================================================
    # Todo lo que estaba acá antes relacionado a VTubers + DB
    # (guardar, actualizar estado, reset live, etc.)
    # SE ELIMINA del bot.
    #
    # Es responsabilidad EXCLUSIVA de n8n.

    @staticmethod
    def get_vtubers_by_ids(vtuber_ids: list[int]) -> list[dict]:
        if not vtuber_ids:
            return []

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        placeholders = ",".join(["%s"] * len(vtuber_ids))
        cursor.execute(f"""
            SELECT id AS vtuber_id,
                platform,
                login_name,
                display_name_text,
                avatar_url,
                language,
                is_vtuber
            FROM vtubers
            WHERE id IN ({placeholders})
        """, vtuber_ids)

        rows = cursor.fetchall()
        conn.close()
        return rows

    @staticmethod
    def get_followers(vtuber_id: int) -> list[int]:
        """
        Devuelve una lista de user_id que siguen a la vtuber
        """
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT user_id
            FROM vtuber_follows
            WHERE vtuber_id = %s
            """,
            (vtuber_id,)
        )

        rows = cursor.fetchall()
        conn.close()

        # rows = [(123,), (456,), ...]
        return [row[0] for row in rows]
    
    @staticmethod
    def get_notify_channel(guild_id: int) -> int | None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT notify_channel_id
            FROM server_config
            WHERE guild_id = %s
            """,
            (guild_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return int(row[0])


    @staticmethod
    def get_notify_channel(guild_id: int) -> int | None:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT notify_channel_id
            FROM server_config
            WHERE guild_id = %s
            """,
            (guild_id,)
        )

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return int(row[0])
    
    @staticmethod
    def set_notify_channel(guild_id: int, channel_id: int):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO server_config (guild_id, notify_channel_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
            notify_channel_id = VALUES(notify_channel_id)
            """,
            (guild_id, channel_id)
        )

        conn.commit()
        conn.close()

    @staticmethod
    def get_stream_status(vtuber_id: int) -> dict | None:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                is_live,
                stream_title,
                category,
                viewer_count
            FROM vtuber_stream_status
            WHERE vtuber_id = %s
            """, (vtuber_id,))

        row = cursor.fetchone()
        conn.close()
        return row
    
    @staticmethod
    def user_follows_vtuber(user_id: int, vtuber_id: int) -> bool:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 1
            FROM vtuber_follows
            WHERE user_id = %s AND vtuber_id = %s
            LIMIT 1
        """, (user_id, vtuber_id))

        result = cursor.fetchone()
        conn.close()

        return result is not None


    #FOLLOWS EN /BUSCAR

    @staticmethod
    def follow_vtuber(user_id: int, vtuber_id: int):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT IGNORE INTO vtuber_follows (user_id, vtuber_id)
            VALUES (%s, %s)
        """, (user_id, vtuber_id))

        conn.commit()
        conn.close()

    @staticmethod
    def unfollow_vtuber(user_id: int, vtuber_id: int):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM vtuber_follows
            WHERE user_id = %s AND vtuber_id = %s
        """, (user_id, vtuber_id))

        conn.commit()
        conn.close()

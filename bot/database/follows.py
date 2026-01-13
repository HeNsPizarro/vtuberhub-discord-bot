from bot.database.db import get_connection

def follow_vtuber(user_id: int, vtuber_id: int) -> bool:
    """
    Devuelve True si se creó el follow.
    Devuelve False si ya existía.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT IGNORE INTO vtuber_follows (user_id, vtuber_id)
        VALUES (%s, %s)
    """, (user_id, vtuber_id))

    created = cursor.rowcount > 0

    conn.commit()
    conn.close()
    return created


def unfollow_vtuber(user_id: int, vtuber_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM vtuber_follows
        WHERE user_id = %s AND vtuber_id = %s
    """, (user_id, vtuber_id))

    deleted = cursor.rowcount > 0

    conn.commit()
    conn.close()
    return deleted


def get_followed_vtubers(user_id: int) -> list[int]:
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vtuber_id
        FROM vtuber_follows
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [row[0] for row in rows]


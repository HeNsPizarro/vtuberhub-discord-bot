CREATE TABLE vtubers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT UNIQUE NOT NULL,
    agencia TEXT,
    estado TEXT,
    descripcion TEXT,
    imagen TEXT,
    youtube TEXT,
    twitch TEXT,
    twitter TEXT,
    live INTEGER,
    plataforma TEXT,
    stream_url TEXT
);

CREATE TABLE vtuber_follows (
    user_id TEXT NOT NULL,
    vtuber_nombre TEXT NOT NULL,
    UNIQUE(user_id, vtuber_nombre)
);

CREATE TABLE server_config (
    guild_id TEXT PRIMARY KEY,
    notify_channel_id TEXT
);

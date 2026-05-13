[readme (1) (1).md](https://github.com/user-attachments/files/27675663/readme.1.1.md)
# 🤖 VTuberInfoBot

Bot de Discord orientado a VTubers, diseñado para **buscar información**, **seguir VTubers**, **mostrar quién está en vivo** y **enviar notificaciones automáticas** cuando una VTuber comienza stream.

El sistema está pensado con una **arquitectura profesional**, usando **MySQL como fuente de verdad** y **n8n** como motor de ingesta y actualización de datos desde Twitch.

---

##  Arquitectura General

```
Usuario Discord
   ↓
Bot Discord (Python)
   ↓ HTTP
Webhook interno (aiohttp)
   ↓
Base de Datos MySQL  ← n8n ← Twitch API
```

- El **bot NO consulta Twitch directamente**
- Toda la información proviene de la **base de datos**
- n8n se encarga de:
  - consultar Twitch
  - normalizar datos
  - actualizar estados
  - disparar notificaciones

---

##  Base de Datos

### Tabla: `vtubers`
Fuente principal de datos de VTubers.

Campos clave:
- `id` (PK)
- `platform` (ej: twitch)
- `platform_user_id`
- `login_name`
- `display_name_text`
- `avatar_url`
- `description`
- `language`
- `is_vtuber`
- `created_at`, `updated_at`

---

### Tabla: `vtuber_stream_status`
Estado en tiempo real del stream.

Campos clave:
- `vtuber_id` (FK)
- `is_live`
- `stream_id`
- `stream_title`
- `category`
- `viewer_count`
- `live_started_at`

Se actualiza automáticamente por n8n cada pocos minutos.

---

### Tabla: `vtuber_follows`
Relación usuario ↔ vtuber.

Campos:
- `user_id` (Discord ID)
- `vtuber_id`
- `created_at`

Restricción:
- `UNIQUE(user_id, vtuber_id)`

---

### Tabla: `server_config`
Configuración por servidor.

Campos:
- `guild_id`
- `notify_channel_id`

---

##  Comandos Disponibles

### 🔍 `/vtuber buscar <login>`
Busca una VTuber.

- Si no existe en DB → n8n la carga automáticamente
- Devuelve embed con:
  - avatar
  - descripción
  - plataforma
  - idioma (si existe)
  - estado en vivo

---

### ⭐ `/vtuber follow <login>`
Seguir una VTuber.

- Guarda la relación en DB
- Habilita notificaciones

---

### ❌ `/vtuber unfollow <login>`
Dejar de seguir una VTuber.

---

### 💙 `/vtuber follows`
Lista tus VTubers seguidas.

---

### 🔴 `/vtuber online`
Muestra VTubers en vivo.

Modos:
- Todos
- Seguidos
- Top viewers

---

### 📣 `/setchannel`
Configura el canal de notificaciones del servidor.

---

## 🔔 Sistema de Notificaciones

- n8n detecta transición **offline → online**
- Envía payload HTTP al bot
- El bot:
  - verifica seguidores
  - filtra por servidor
  - menciona solo a usuarios que siguen esa VTuber
  - envía embed de stream en vivo

---

##  Servicios Importantes

### `VTuberService`
Capa de acceso a datos.

Responsabilidades:
- buscar vtubers
- seguir / dejar de seguir
- obtener seguidores
- obtener canal de notificaciones
- actualizar estado live

---

##  Stack Tecnológico

- Python 3.11
- discord.py (app_commands)
- aiohttp
- MySQL / MariaDB
- n8n
- Twitch API

---

##  Estado del Proyecto

✔ Arquitectura estable
✔ Base de datos centralizada
✔ Comandos funcionales
✔ Notificaciones inteligentes
✔ Preparado para escalar

Pendiente:
- `/links`
- mejoras UX
- panel web opcional

---

##  Filosofía

Este bot está diseñado como un **sistema vivo**, no como un bot simple.

- El conocimiento crece con el uso
- Los datos se reutilizan
- El usuario nunca ve la complejidad

---

Hecho con ❤️ y muchas horas de debugging.


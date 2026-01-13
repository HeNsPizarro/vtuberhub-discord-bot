# 🧠 Arquitectura del sistema

Este documento describe la arquitectura actual de **VTuberInfoBot**, explicando cómo se separan responsabilidades entre el bot de Discord, la base de datos y el backend en **n8n**.

---

## 🎯 Objetivo de la arquitectura

- Evitar lógica pesada dentro del bot
- Desacoplar consultas externas y eventos
- Permitir escalabilidad sin reescrituras
- Mantener comandos rápidos y confiables

---

## 🧩 Componentes principales

### 🤖 Bot de Discord (Python)

Responsabilidades:
- Manejar slash commands
- Construir embeds y vistas
- Gestionar follows por usuario
- Enviar notificaciones a servidores
- Persistir estado mínimo en SQLite

El bot **no consulta APIs externas directamente**.

---

### 🗄️ Base de datos (SQLite)

Uso principal:
- Cache de información de VTubers
- Estado de live/offline
- Datos del último stream (title, game, viewers, etc.)
- Follows por usuario
- Configuración de canal por servidor

📌 No se utiliza para consultas en tiempo real.

---

### 🧠 Backend n8n

n8n funciona como backend desacoplado y orquestador de eventos.

Responsabilidades:
- Consultar APIs externas (Twitch, etc.)
- Detectar cambios OFFLINE → LIVE
- Enviar eventos al bot vía Webhooks
- Responder consultas en tiempo real para comandos

---

## 🔁 Flujos principales

### 🔔 Flujo de notificaciones automáticas

```
Schedule Trigger (cron)
→ Consultas a APIs (n8n)
→ Detección OFFLINE → LIVE
→ Webhook al bot (/vtuber/live)
→ Actualización de estado en DB
→ Envío de embed al canal configurado
```

Características:
- Se ejecuta periódicamente
- Guarda estado
- Una notificación por stream
- Evita spam

---

### ⚡ Flujo del comando `/vtuber online`

```
Discord command
→ Bot
→ Webhook a n8n (/vtuber/online)
→ Consulta en tiempo real a APIs
→ Respuesta JSON
→ Embed en Discord
```

Características:
- No usa la base de datos
- No guarda estado
- Siempre muestra información actual

---

### 🔍 Flujo del comando `/vtuber buscar`

```
Discord command
→ Bot
→ Consulta SQLite
→ (si no existe) Webhook a n8n
→ Guardado en DB
→ Embed en Discord
```

---

## 🧠 Decisiones de diseño importantes

- Separación estricta entre:
  - **Comandos** (consultas)
  - **Notificaciones** (eventos)

- Los workflows de n8n:
  - o **guardan estado**
  - o **responden datos**, pero nunca ambas cosas

- `/vtuber online` es el único comando 100% tiempo real

- No se envían mensajes privados por defecto

- Cada servidor administra su propio canal de notificaciones

---

## 📐 Beneficios de esta arquitectura

- Menos bugs por estados inconsistentes
- Fácil de extender (nuevas plataformas, eventos)
- Comandos rápidos y predecibles
- Backend reutilizable

---

Documentación actualizada – VTuberInfoBot


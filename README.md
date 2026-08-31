# Ghost Gang Discord Bot

A small `discord.py` bot for GHOST EMPIRE. It includes slash-command support, sends a welcome embed whenever a new member joins, and exposes a health endpoint for deployment monitoring.

## Run it

1. Add your Discord bot token to Replit Secrets with the key `DISCORD_TOKEN`.
2. Invite the bot to your server with the `bot` and `applications.commands` scopes.
3. Give it permission to:
   - View the welcome channel
   - Send Messages
   - Embed Links
4. Enable **Server Members Intent** for the bot in the Discord Developer Portal.
5. Start the **Ghost Gang Bot** workflow.
6. In your server, run `/setwelcome` and select the welcome channel.

The selected channel is saved in `welcome_config.json`, separately for each server.

The bot also starts a keep-alive health server on port `8080` (or the `PORT` environment variable when one is provided). It responds with a healthy JSON status at `/health`.

## Slash command

- `/setwelcome channel:<channel>` — sets where new-member welcome embeds are sent. The command requires the **Manage Server** permission.
- `/setprices` — posts the GHOST EMPIRE developer-prices embed in the current channel. The command requires the **Manage Server** permission.

## Welcome message

The bot sends a red embed with:

- **Title:** `👑 GHOST GANG ME ENTRY 👑`
- **Description:**
  ```
  Yo @member Welcome mitar! 💀

  Tu hamara {count}th member hai GHOST EMPIRE ka!

  📌 Rule padh le - 📜︱rules
  📌 Announcement check kar le - 🍁︱announcement
  📌 Ranks dekh le - 🛒︱ranks

  Ab mauj kar mitar! 🔥
  ```

## Developer prices

`/setprices` posts a gold embed with the current DC, Minecraft, and bot developer prices.
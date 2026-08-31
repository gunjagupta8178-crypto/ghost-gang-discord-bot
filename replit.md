# Ghost Gang Discord Bot

A simple `discord.py` bot that configures a per-server welcome channel with `/setwelcome` and greets new members with a GHOST EMPIRE embed.

## Run & Operate

- Start the `Ghost Gang Bot` workflow, which runs `python main.py`.
- Required secret: `DISCORD_TOKEN`.
- The bot exposes a keep-alive health endpoint on port `8080`.
- Enable the Discord **Server Members Intent** before running the bot.
- Use `/setwelcome` in a server to select the welcome channel.

## Stack

- Python 3.11
- `discord.py`
- JSON file persistence for per-server welcome-channel settings

## Where things live

- `main.py` — bot implementation, slash command, and welcome handler
- `welcome_config.json` — created at runtime after `/setwelcome` is used
- `README.md` — setup and Discord permission checklist

## Architecture decisions

- Global slash-command sync keeps the bot simple and makes `/setwelcome` available in every installed server.
- Welcome settings are stored in JSON because this bot needs only one small setting per guild.
- The bot requests the `members` intent because member-join events require it.

## Product

- Server managers choose a welcome channel with `/setwelcome`.
- New members receive the requested Ghost Empire welcome embed.

## User preferences

- Keep the bot simple and runnable.

## Gotchas

- `DISCORD_TOKEN` must be set as a secret; never commit it to a file.
- The Server Members Intent must be enabled in the Discord Developer Portal and in `main.py`.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details

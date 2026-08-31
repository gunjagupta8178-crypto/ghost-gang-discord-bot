from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("ghost-gang-bot")

CONFIG_PATH = Path("welcome_config.json")
KEEP_ALIVE_PORT = int(os.getenv("PORT", "8080"))


class KeepAliveHandler(BaseHTTPRequestHandler):
    """Small health server for deployment health checks."""

    def do_GET(self) -> None:
        if self.path not in {"/", "/health"}:
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        response = b'{"status":"ok","service":"ghost-gang-discord-bot"}\n'
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format: str, *args: Any) -> None:
        logger.info("Keep-alive request: " + format, *args)


def start_keep_alive_server() -> None:
    """Run an HTTP health endpoint without blocking the Discord bot."""
    server = ThreadingHTTPServer(("0.0.0.0", KEEP_ALIVE_PORT), KeepAliveHandler)
    logger.info("Keep-alive server listening on port %d.", KEEP_ALIVE_PORT)
    server.serve_forever()


def load_welcome_channels() -> dict[str, int]:
    """Load guild welcome-channel IDs from disk."""
    if not CONFIG_PATH.exists():
        return {}

    try:
        raw_config: Any = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("Could not read %s; starting with no welcome channels.", CONFIG_PATH)
        return {}

    if not isinstance(raw_config, dict):
        return {}

    return {
        str(guild_id): int(channel_id)
        for guild_id, channel_id in raw_config.items()
        if str(guild_id).isdigit() and str(channel_id).isdigit()
    }


def save_welcome_channels(channels: dict[str, int]) -> None:
    """Persist guild welcome-channel IDs in a small, human-readable JSON file."""
    CONFIG_PATH.write_text(
        json.dumps(channels, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


class GhostGangBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(command_prefix="!", intents=intents)
        self.welcome_channels = load_welcome_channels()
        self._commands_synced = False

    async def setup_hook(self) -> None:
        # Global slash commands are available in every server where the bot is installed.
        if not self._commands_synced:
            synced_commands = await self.tree.sync()
            self._commands_synced = True
            logger.info("Synced %d slash command(s).", len(synced_commands))

    async def on_ready(self) -> None:
        if self.user is not None:
            logger.info("Logged in as %s (%s).", self.user, self.user.id)
        logger.info("Connected to %d server(s).", len(self.guilds))

    async def on_member_join(self, member: discord.Member) -> None:
        channel_id = self.welcome_channels.get(str(member.guild.id))
        if channel_id is None:
            return

        channel = member.guild.get_channel(channel_id)
        if not isinstance(channel, discord.TextChannel):
            logger.warning(
                "Welcome channel %s is missing or is not a text channel in %s.",
                channel_id,
                member.guild.name,
            )
            return

        count = member.guild.member_count or len(member.guild.members)
        embed = discord.Embed(
            title="👑 GHOST GANG ME ENTRY 👑",
            description=(
                f"Yo {member.mention} Welcome mitar! 💀\n\n"
                f"Tu hamara {count}th member hai GHOST EMPIRE ka!\n\n"
                "📌 Rule padh le - 📜︱rules\n"
                "📌 Announcement check kar le - 🍁︱announcement\n"
                "📌 Ranks dekh le - 🛒︱ranks\n\n"
                "Ab mauj kar mitar! 🔥"
            ),
            color=discord.Color.red(),
        )

        try:
            await channel.send(embed=embed)
        except discord.Forbidden:
            logger.warning("Missing permission to send welcome message in #%s.", channel.name)
        except discord.HTTPException:
            logger.exception("Discord rejected the welcome message in #%s.", channel.name)


bot = GhostGangBot()


def build_prices_embed() -> discord.Embed:
    return discord.Embed(
        title="🛒 GHOST EMPIRE - DEVELOPER PRICES 💀",
        description=(
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "💎 **DC DEVELOPER**\n"
            "> Price: **₹99 Only**\n"
            "> Full Discord Server Setup\n\n"
            "⛏️ **MINECRAFT SERVER DEVELOPER**\n"
            "> Price: **COMING SOON ⏳**\n"
            "> Stay Tuned!\n\n"
            "🤖 **BOT DEVELOPER**\n"
            "> Price: **₹800 Only**\n"
            "> Custom Discord Bot\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "📩 DM Owner to Buy!\n"
            "💀 GHOST EMPIRE - Best Quality!"
        ),
        color=discord.Color.gold(),
    )


@bot.tree.command(name="setwelcome", description="Set the channel for new-member welcome messages.")
@app_commands.describe(channel="The text channel where welcome embeds should be sent.")
@app_commands.default_permissions(manage_guild=True)
async def setwelcome(interaction: discord.Interaction, channel: discord.TextChannel) -> None:
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True,
        )
        return

    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "You need the Manage Server permission to use this command.",
            ephemeral=True,
        )
        return

    bot.welcome_channels[str(interaction.guild.id)] = channel.id
    try:
        save_welcome_channels(bot.welcome_channels)
    except OSError:
        logger.exception("Could not save the welcome-channel setting.")
        await interaction.response.send_message(
            "I couldn't save that setting. Check the bot's file permissions.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(
        f"Welcome messages will now be sent in {channel.mention}.",
        ephemeral=True,
    )


@bot.tree.command(name="setprices", description="Post the GHOST EMPIRE developer prices embed.")
@app_commands.default_permissions(manage_guild=True)
async def setprices(interaction: discord.Interaction) -> None:
    if interaction.guild is None:
        await interaction.response.send_message(
            "This command can only be used inside a server.",
            ephemeral=True,
        )
        return

    if not isinstance(interaction.user, discord.Member) or not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message(
            "You need the Manage Server permission to use this command.",
            ephemeral=True,
        )
        return

    await interaction.response.send_message(embed=build_prices_embed())


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError(
            "DISCORD_TOKEN is missing. Add it to Replit Secrets before starting the bot."
        )

    Thread(target=start_keep_alive_server, name="keep-alive", daemon=True).start()
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    main()

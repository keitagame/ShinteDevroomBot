import discord
from discord import app_commands
from discord.ext import commands


class Ping(commands.Cog):
    """動作確認用の最小サンプル Cog"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # テキストコマンド（!ping）
    @commands.command(name="ping")
    async def ping(self, ctx: commands.Context):
        latency_ms = round(self.bot.latency * 1000)
        await ctx.send(f"Pong! ({latency_ms}ms)")

    # スラッシュコマンド（/ping）
    @app_commands.command(name="ping", description="Botの応答速度を確認します")
    async def ping_slash(self, interaction: discord.Interaction):
        latency_ms = round(self.bot.latency * 1000)
        await interaction.response.send_message(f"Pong! ({latency_ms}ms)")


async def setup(bot: commands.Bot):
    await bot.add_cog(Ping(bot))

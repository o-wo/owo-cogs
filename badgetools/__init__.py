from discord.utils import maybe_coroutine

from .badgetools import BadgeTools

__red_end_user_data_statement__ = "This cog does not persistently store any PII data about users."

async def setup(bot):
    await maybe_coroutine(bot.add_cog, BadgeTools())

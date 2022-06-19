import aiohttp
import asyncio

from io import BytesIO
from typing import Literal, Optional

import discord
from redbot.core import commands

MAP_TYPES = ["roadmap", "satellite", "terrain", "hybrid"]


class Maps(commands.Cog):
    """Fetch a Google map of a specific location."""

    __authors__ = ["ow0x"]
    __version__ = "1.0.0"

    def format_help_for_context(self, ctx: commands.Context) -> str:
        """Thanks Sinbad."""
        return (
            f"{super().format_help_for_context(ctx)}\n\n"
            f"Authors:  {', '.join(self.__authors__)}\n"
            f"Cog version:  v{self.__version__}"
        )

    @commands.command()
    @commands.is_owner()
    @commands.bot_has_permissions(attach_files=True)
    async def map(
        self,
        ctx: commands.Context,
        zoom: Optional[int],
        maptype: Literal["roadmap", "satellite", "terrain", "hybrid"],
        *,
        location: str
    ):
        """Fetch a Google map of a specific location in various modes.

        `zoom` parameter accepts values between 1 and 20

        The following list shows the approximate level of detail you can expect to see at each zoom level:
        ```
        1  : World
        5  : Landmass/continent
        10 : City
        15 : Streets
        20 : Buildings
        ```

        `maptype` parameter accepts 4 formats:
        ```
        roadmap, satellite, terrain, hybrid
        ```
        You can read more on that in detail on Google Developers docs:
        https://developers.google.com/maps/documentation/maps-static/start#MapTypes

        ⚠️ This command requires a Google Maps API key, if you have one, set it with:
        ```
        [p]set api googlemaps api_key <api_key>
        ```
        """
        api_key = (await ctx.bot.get_shared_api_tokens("googlemaps")).get("api_key")
        if not api_key:
            return await ctx.send_help()

        zoom = zoom if (zoom and 1 <= zoom <= 20) else 12
        maptype = "roadmap" if maptype not in MAP_TYPES else maptype

        async with ctx.typing():
            base_url = "https://maps.googleapis.com/maps/api/staticmap"
            params = {
                "zoom": zoom,
                "size": "500x500",
                "scale": "2",
                "maptype": maptype,
                "center": location,
                "key": api_key
            }
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(base_url, params=params) as response:
                        if response.status != 200:
                            await ctx.send(f"https://http.cat/{response.status}")
                            return
                        image = BytesIO(await response.read())
                        image.seek(0)
            except asyncio.TimeoutError:
                return await ctx.send("Operation timed out.")

            url = f"<https://www.google.com/maps/search/{location.replace(' ', '+')}>"
            await ctx.send(content=url, file=discord.File(image, "map.png"))

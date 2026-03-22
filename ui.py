from enum import Enum
import discord


class RenderStatus(Enum):
    QUEUED = "Queued", discord.colour.Colour.blue()
    PROCESSING = "Processing", discord.colour.Colour.blue()
    ERROR = "Error: ", discord.colour.Colour.red()
    SUCCESS = "Done", discord.colour.Colour.green()


def create_embed(
    replay: discord.Attachment, status: RenderStatus, *, error_msg: str = ""
) -> discord.Embed:
    embed = discord.Embed(title=replay.filename, url=replay.url, colour=status.value[1])

    if status is RenderStatus.ERROR:
        embed.add_field(name="Status", value=status.value[0] + error_msg)
    else:
        embed.add_field(name="Status", value=status.value[0])

    return embed

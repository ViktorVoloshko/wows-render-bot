import discord
import asyncio
import logging
import tempfile

from pathlib import Path
from subprocess import SubprocessError


from render import render_replay
import ui
import config


async def start():
    semaphore = asyncio.Semaphore(config.CONCURRENT_JOBS)
    bot = discord.Bot()

    @bot.event
    async def on_ready():
        logging.info(f"{bot.user} ready")

    @bot.slash_command(name="render", description="Render replay")
    async def render(ctx: discord.ApplicationContext, attachment: discord.Attachment):
        logging.info(
            f"got {attachment.filename} from {ctx.author.name} [{ctx.author.id}]"
        )

        if not attachment.filename.endswith(".wowsreplay"):
            logging.info(f"bad file {attachment.filename}")
            await ctx.response.send_message(
                embed=ui.create_embed(
                    attachment, ui.RenderStatus.ERROR, error_msg="not a replay"
                )
            )
            return

        logging.info(f"queued {attachment.filename}")
        msg = await ctx.response.send_message(
            embed=ui.create_embed(attachment, ui.RenderStatus.QUEUED)
        )

        async with semaphore:
            logging.info(f"processing {attachment.filename}")
            await msg.edit(
                embed=ui.create_embed(attachment, ui.RenderStatus.PROCESSING)
            )

            with tempfile.TemporaryDirectory() as tmpdir:
                logging.info(f"created {tmpdir} for {attachment.filename}")

                tmpdir_path = Path(tmpdir)
                await attachment.save(Path(tmpdir_path / attachment.filename))
                try:
                    await render_replay(
                        tmpdir_path / attachment.filename,
                        tmpdir_path / f"{attachment.title}.mp4",
                        config.FILESIZE_LIMIT * 1024 * 1024,
                    )
                except SubprocessError as e:
                    logging.error(f"failed processing {attachment.filename}")
                    await msg.edit(
                        embed=ui.create_embed(
                            attachment, ui.RenderStatus.ERROR, error_msg=str(e)
                        )
                    )
                else:
                    logging.info(f"done processing {attachment.filename}")
                    await msg.edit(
                        embed=ui.create_embed(attachment, ui.RenderStatus.SUCCESS),
                        file=discord.File(f"{tmpdir_path / str(attachment.title)}.mp4"),
                    )

    await bot.start(config.DISCORD_TOKEN)

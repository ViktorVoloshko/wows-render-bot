import asyncio
import logging
import os

from pathlib import Path
from subprocess import SubprocessError


async def render_replay(replay_path: Path, video_path: Path, filesize_limit: int):
    crf_value = 17

    while True:
        logging.info(f"rendering {replay_path} with crf {crf_value}")

        frames_read, frames_write = os.pipe()

        renderer_proc = await asyncio.create_subprocess_exec(
            "minimap_renderer",
            "--cpu",
            "--extracted-dir",
            "wows_extr",
            "--dump-frames",
            "-o",
            "temp.mp4",
            replay_path,
            stdout=frames_write,
            stderr=asyncio.subprocess.PIPE,
        )

        ffmpeg_proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-f",
            "image2pipe",
            "-framerate",
            "30",
            "-i",
            "pipe:0",
            "-threads",
            "1",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            str(crf_value),
            "-y",
            video_path,
            stdin=frames_read,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        os.close(frames_write)
        os.close(frames_read)

        stdout, stderr = await renderer_proc.communicate()
        if renderer_proc.returncode != 0:
            logging.error(f"{renderer_proc!r} failed\nstderr\n{stderr.decode()}")
            raise SubprocessError("minimap_renderer failed")

        stdout, stderr = await ffmpeg_proc.communicate()
        if ffmpeg_proc.returncode != 0:
            logging.error(
                f"{ffmpeg_proc!r} failed\nstdout\n{stdout.decode()}\nstderr\n{stderr.decode()}"
            )
            raise SubprocessError("ffmpeg failed")

        if os.path.getsize(video_path) < filesize_limit:
            break

        crf_value += 3

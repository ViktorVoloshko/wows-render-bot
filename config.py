import dotenv
import os
import multiprocessing


DISCORD_TOKEN: str
FILESIZE_LIMIT: int
CONCURRENT_JOBS: int


def init():
    global DISCORD_TOKEN, FILESIZE_LIMIT, CONCURRENT_JOBS

    dotenv.load_dotenv()

    token = os.getenv("DISCORD_TOKEN")
    if token is None:
        raise ValueError("no token")
    DISCORD_TOKEN = token

    match os.getenv("FILESIZE_LIMIT"):
        case None:
            FILESIZE_LIMIT = 8
        case limit:
            FILESIZE_LIMIT = int(limit)

    match os.getenv("CONCURRENT_JOBS"):
        case None:
            CONCURRENT_JOBS = multiprocessing.cpu_count() - 1
        case n:
            CONCURRENT_JOBS = int(n)

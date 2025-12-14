import math
import time


def human_readable_size(size: float) -> str:
    if size == 0:
        return "0B"
    power = 2**10
    n = 0
    units = ["B", "KB", "MB", "GB", "TB"]
    while size > power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f}{units[n]}"


async def progress_for_pyrogram(
    current: int,
    total: int,
    message,
    start_time: float,
    prefix: str = "Uploading"
):
    now = time.time()
    diff = now - start_time
    if diff == 0:
        diff = 1

    percentage = current * 100 / total
    speed = current / diff
    elapsed_time = round(diff)
    eta = round((total - current) / speed) if speed != 0 else 0

    filled_length = int(30 * current // total)
    bar = "█" * filled_length + "░" * (30 - filled_length)

    text = (
        f"{prefix}\n"
        f"[{bar}] {percentage:.2f}%\n"
        f"{human_readable_size(current)} of {human_readable_size(total)}\n"
        f"Speed: {human_readable_size(speed)}/s\n"
        f"Elapsed: {elapsed_time}s | ETA: {eta}s"
    )
    try:
        await message.edit_text(text)
    except Exception:
        pass

import asyncio
from pathlib import Path

RUNNING_PROCESSES = {}


async def start_bot(bot_id: int, script_path: str):

    if bot_id in RUNNING_PROCESSES:
        return False, "Bot already running."

    process = await asyncio.create_subprocess_exec(
        "python3",
        script_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    RUNNING_PROCESSES[bot_id] = process

    return True, "Bot started successfully."


async def stop_bot(bot_id: int):

    process = RUNNING_PROCESSES.get(bot_id)

    if not process:
        return False, "Bot is not running."

    process.terminate()

    await process.wait()

    RUNNING_PROCESSES.pop(bot_id, None)

    return True, "Bot stopped."


async def restart_bot(bot_id: int, script_path: str):

    await stop_bot(bot_id)

    return await start_bot(bot_id, script_path)


async def delete_bot_files(folder: str):

    path = Path(folder)

    if not path.exists():
        return False, "Folder not found."

    for file in path.rglob("*"):

        if file.is_file():
            file.unlink()

    for directory in sorted(path.rglob("*"), reverse=True):

        if directory.is_dir():
            directory.rmdir()

    path.rmdir()

    return True, "Bot deleted."

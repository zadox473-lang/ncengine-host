import shutil
from pathlib import Path

from aiogram import Bot

from config import HOSTED_FOLDER


TEMPLATE_FILE = Path("templates/hosted_script.py")


async def create_hosted_bot(
    bot_token: str,
    owner_id: int,
    name: str,
    bot_username: str,
):
    """
    Create hosted bot files.
    """

    bot_folder = HOSTED_FOLDER / bot_username
    bot_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    bot_file = bot_folder / "bot.py"

    shutil.copy(
        TEMPLATE_FILE,
        bot_file
    )

    content = bot_file.read_text(
        encoding="utf-8"
    )

    content = content.replace(
        "{BOT_TOKEN}",
        bot_token
    )

    content = content.replace(
        "{OWNER_ID}",
        str(owner_id)
    )

    content = content.replace(
        "{NAME}",
        name
    )

    bot_file.write_text(
        content,
        encoding="utf-8"
    )

    return bot_folder, bot_file

from database.users import remove_display_name
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from states import UserSettings
from database.users import (
    update_display_name,
    update_owner_id,
    remove_owner_id,
)
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from keyboards.user import (
    start_keyboard,
    about_keyboard,
    settings_keyboard,
    hosting_keyboard,
)

from database.users import (
    register_user,
    get_user,
)

from config import (
    POWERED_BY,
    CHANNEL_USERNAME,
)

router = Router()


@router.message(CommandStart())
async def start_command(message: Message):

    await register_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    user = await get_user(message.from_user.id)

    display_name = (
        user["display_name"]
        if user and user["display_name"]
        else message.from_user.first_name
    )

    text = f"""
<b>👋 Welcome {display_name}</b>

<b>⚡ NC ENGINE HOST</b>

Host your Telegram bots within seconds.

━━━━━━━━━━━━━━━━━━

🤖 Upload up to <b>10 Bot Tokens</b>

🆔 Set your Owner ID

👤 Set your Display Name

💬 24×7 Support

━━━━━━━━━━━━━━━━━━

{POWERED_BY}
"""

    await message.answer(
        text,
        reply_markup=start_keyboard()
    )


@router.callback_query(F.data == "back_home")
async def back_home(callback: CallbackQuery):

    user = await get_user(callback.from_user.id)

    display_name = (
        user["display_name"]
        if user and user["display_name"]
        else callback.from_user.first_name
    )

    text = f"""
<b>👋 Welcome {display_name}</b>

<b>⚡ NC ENGINE HOST</b>

Host your Telegram bots within seconds.

━━━━━━━━━━━━━━━━━━

🤖 Upload up to <b>10 Bot Tokens</b>

🆔 Set your Owner ID

👤 Set your Display Name

💬 24×7 Support

━━━━━━━━━━━━━━━━━━

{POWERED_BY}
"""

    await callback.message.edit_text(
        text,
        reply_markup=start_keyboard()
    )

    await callback.answer()
@router.callback_query(F.data == "about")
async def about_menu(callback: CallbackQuery):

    text = f"""
<b>⚡ NC ENGINE HOST</b>

Professional Telegram Multi Bot Hosting.

━━━━━━━━━━━━━━━━━━

✅ Host up to 10 Bots

✅ One Click Deployment

✅ Owner ID Support

✅ Custom Display Name

✅ Fast Hosting

✅ 24×7 Support

━━━━━━━━━━━━━━━━━━

📢 Channel : {CHANNEL_USERNAME}

{POWERED_BY}
"""

    await callback.message.edit_text(
        text,
        reply_markup=about_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "settings")
async def settings_menu(callback: CallbackQuery):

    user = await get_user(callback.from_user.id)

    display_name = (
        user["display_name"]
        if user
        else "Not Set"
    )

    owner_id = (
        user["owner_id"]
        if user and user["owner_id"]
        else "Not Set"
    )

    text = f"""
<b>⚙️ Settings</b>

━━━━━━━━━━━━━━━━━━

👤 Name :
<code>{display_name}</code>

🆔 Owner ID :
<code>{owner_id}</code>

━━━━━━━━━━━━━━━━━━

Choose an option below.
"""

    await callback.message.edit_text(
        text,
        reply_markup=settings_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "host_bots")
async def host_bots(callback: CallbackQuery):

    user = await get_user(callback.from_user.id)

    hosted = user["hosted_count"] if user else 0

    text = f"""
<b>🤖 Bot Hosting</b>

━━━━━━━━━━━━━━━━━━

Hosted Bots :
<b>{hosted}/10</b>

━━━━━━━━━━━━━━━━━━

• Upload 10 Bot Tokens

• Tokens must be valid.

• After verification your bots
will automatically be hosted.

━━━━━━━━━━━━━━━━━━

{POWERED_BY}
"""

    await callback.message.edit_text(
        text,
        reply_markup=hosting_keyboard()
    )

    await callback.answer()


@router.callback_query(F.data == "my_hosting")
async def my_hosting(callback: CallbackQuery):

    user = await get_user(callback.from_user.id)

    hosted = user["hosted_count"] if user else 0

    owner = (
        user["owner_id"]
        if user and user["owner_id"]
        else "Not Set"
    )

    text = f"""
<b>📂 My Hosting</b>

━━━━━━━━━━━━━━━━━━

🤖 Hosted Bots :
<b>{hosted}/10</b>

🆔 Owner ID :
<code>{owner}</code>

━━━━━━━━━━━━━━━━━━

Manage your bots from
the hosting panel.

{POWERED_BY}
"""

    await callback.message.edit_text(
        text,
        reply_markup=hosting_keyboard()
    )

    await callback.answer()
  @router.callback_query(F.data == "set_name")
async def set_name(callback: CallbackQuery, state: FSMContext):

    await state.set_state(UserSettings.waiting_for_name)

    await callback.message.edit_text(
        "<b>👤 Send your display name.</b>\n\nMaximum 30 characters."
    )

    await callback.answer()


@router.message(UserSettings.waiting_for_name)
async def save_name(message: Message, state: FSMContext):

    name = message.text.strip()

    if len(name) > 30:

        await message.answer(
            "❌ Maximum length is 30 characters."
        )

        return

    await update_display_name(
        message.from_user.id,
        name
    )

    await state.clear()

    await message.answer(
        f"✅ Display Name Updated\n\n<b>{name}</b>",
        reply_markup=start_keyboard()
    )


@router.callback_query(F.data == "set_owner")
async def set_owner(callback: CallbackQuery, state: FSMContext):

    await state.set_state(UserSettings.waiting_for_owner)

    await callback.message.edit_text(
        "<b>🆔 Send your Telegram User ID.</b>"
    )

    await callback.answer()


@router.message(UserSettings.waiting_for_owner)
async def save_owner(message: Message, state: FSMContext):

    if not message.text.isdigit():

        await message.answer(
            "❌ Invalid User ID."
        )

        return

    owner_id = int(message.text)

    await update_owner_id(
        message.from_user.id,
        owner_id
    )

    await state.clear()

    await message.answer(
        f"✅ Owner ID Saved\n\n<code>{owner_id}</code>",
        reply_markup=start_keyboard()
    )


@router.callback_query(F.data == "remove_owner")
async def delete_owner(callback: CallbackQuery):

    await remove_owner_id(callback.from_user.id)

    await callback.message.edit_text(
        "✅ Owner ID Removed.",
        reply_markup=start_keyboard()
    )

    await callback.answer()

@router.callback_query(F.data == "remove_name")
async def delete_name(callback: CallbackQuery):

    await remove_display_name(callback.from_user.id)

    await callback.message.edit_text(
        "✅ Display Name Removed.",
        reply_markup=start_keyboard()
    )

    await callback.answer()

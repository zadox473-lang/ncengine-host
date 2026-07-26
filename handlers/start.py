# handlers/start.py
# Welcome screen handler for NC ENGINE HOST

from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.fsm.state import State, StatesGroup

from database.users import UserDB
from utils.logger import logger

router = Router()
user_db = UserDB()

# ==================== STATES ====================
class StartStates(StatesGroup):
    main_menu = State()

# ==================== KEYBOARDS ====================
def get_main_menu() -> InlineKeyboardMarkup:
    """Main menu keyboard for NC ENGINE HOST"""
    keyboard = [
        [InlineKeyboardButton(text="👤 Profile", callback_data="profile_menu")],
        [InlineKeyboardButton(text="🤖 My Bots", callback_data="my_bots")],
        [InlineKeyboardButton(text="📤 Upload Tokens", callback_data="upload_tokens")],
        [InlineKeyboardButton(text="🎫 Support", callback_data="support_menu")],
        [InlineKeyboardButton(text="📢 Channel", url="https://t.me/proxydominates")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# ==================== START COMMAND ====================
@router.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    """Handle /start command - show welcome screen"""
    user_id = message.from_user.id
    username = message.from_user.username or "NoUsername"
    first_name = message.from_user.first_name or "User"
    
    # Save or update user in database
    await user_db.create_or_update_user(
        user_id=user_id,
        username=username,
        first_name=first_name
    )
    
    # Clear any existing state
    await state.clear()
    await state.set_state(StartStates.main_menu)
    
    # Get user data
    user_data = await user_db.get_user(user_id)
    name = user_data.get("display_name", "Not Set") if user_data else "Not Set"
    owner_id = user_data.get("owner_id", "Not Set") if user_data else "Not Set"
    
    # Welcome message
    welcome_text = f"""⚡ **NC ENGINE HOST** ⚡

👤 **Your Profile:**
• Name: `{name}`
• Owner ID: `{owner_id}`

━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 **Host your Telegram bots easily!**

• Upload up to 10 bot tokens
• Manage all bots from one panel
• Professional hosting

━━━━━━━━━━━━━━━━━━━━━━━━━━
📢 Channel: @proxydominates
🆘 Support: @ncenginehost_bot

Powered By @proxydominates"""
    
    # Main menu keyboard
    keyboard = get_main_menu()
    
    await message.answer(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    
    logger.info(f"User {user_id} (@{username}) started the bot")


# ==================== MAIN MENU CALLBACK ====================
@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Return to main menu"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user_data = await user_db.get_user(user_id)
    
    name = user_data.get("display_name", "Not Set") if user_data else "Not Set"
    owner_id = user_data.get("owner_id", "Not Set") if user_data else "Not Set"
    
    welcome_text = f"""⚡ **NC ENGINE HOST** ⚡

👤 **Your Profile:**
• Name: `{name}`
• Owner ID: `{owner_id}`

━━━━━━━━━━━━━━━━━━━━━━━━━━

🤖 **Host your Telegram bots easily!**

• Upload up to 10 bot tokens
• Manage all bots from one panel
• Professional hosting

━━━━━━━━━━━━━━━━━━━━━━━━━━
📢 Channel: @proxydominates
🆘 Support: @ncenginehost_bot

Powered By @proxydominates"""
    
    keyboard = get_main_menu()
    
    await callback.message.edit_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ==================== PROFILE MENU ====================
@router.callback_query(F.data == "profile_menu")
async def profile_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Show profile menu"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user_data = await user_db.get_user(user_id)
    
    name = user_data.get("display_name", "Not Set") if user_data else "Not Set"
    owner_id = user_data.get("owner_id", "Not Set") if user_data else "Not Set"
    
    profile_text = f"""👤 **Your Profile**

📛 **Name:** `{name}`
🆔 **Owner ID:** `{owner_id}`
🆔 **User ID:** `{user_id}`

━━━━━━━━━━━━━━━━━━━━━━━━━━

What would you like to do?"""
    
    keyboard = [
        [InlineKeyboardButton(text="📝 Set Name", callback_data="set_name")],
        [InlineKeyboardButton(text="❌ Unset Name", callback_data="unset_name")],
        [InlineKeyboardButton(text="🆔 Set Owner ID", callback_data="set_owner_id")],
        [InlineKeyboardButton(text="❌ Unset Owner ID", callback_data="unset_owner_id")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        profile_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ==================== SET NAME ====================
@router.callback_query(F.data == "set_name")
async def set_name_callback(callback: CallbackQuery, state: FSMContext):
    """Ask user for display name"""
    await callback.answer()
    await state.set_state("waiting_for_name")
    
    await callback.message.edit_text(
        "📝 **Set Your Display Name**\n\n"
        "Send me your display name.\n"
        "This name will appear on your hosted bots.\n\n"
        "Example: `Asmit`\n\n"
        "🔙 Send /cancel to cancel.",
        parse_mode="Markdown"
    )


# ==================== UNSET NAME ====================
@router.callback_query(F.data == "unset_name")
async def unset_name_callback(callback: CallbackQuery, state: FSMContext):
    """Unset user's display name"""
    await callback.answer()
    
    user_id = callback.from_user.id
    await user_db.update_user(user_id, display_name=None)
    
    await callback.message.edit_text(
        "✅ **Name has been removed!**\n\n"
        "Your profile name is now empty.",
        parse_mode="Markdown"
    )
    
    # Go back to profile
    await profile_menu_callback(callback, state)


# ==================== SET OWNER ID ====================
@router.callback_query(F.data == "set_owner_id")
async def set_owner_id_callback(callback: CallbackQuery, state: FSMContext):
    """Ask user for owner ID"""
    await callback.answer()
    await state.set_state("waiting_for_owner_id")
    
    await callback.message.edit_text(
        "🆔 **Set Your Owner ID**\n\n"
        "Send me your Telegram User ID.\n"
        "This ID will be the owner of your hosted bots.\n\n"
        "Example: `5661889723`\n\n"
        "🔙 Send /cancel to cancel.",
        parse_mode="Markdown"
    )


# ==================== UNSET OWNER ID ====================
@router.callback_query(F.data == "unset_owner_id")
async def unset_owner_id_callback(callback: CallbackQuery, state: FSMContext):
    """Unset user's owner ID"""
    await callback.answer()
    
    user_id = callback.from_user.id
    await user_db.update_user(user_id, owner_id=None)
    
    await callback.message.edit_text(
        "✅ **Owner ID has been removed!**\n\n"
        "Your bot owner ID is now empty.",
        parse_mode="Markdown"
    )
    
    # Go back to profile
    await profile_menu_callback(callback, state)


# ==================== HANDLE NAME INPUT ====================
@router.message(StateFilter("waiting_for_name"))
async def handle_name_input(message: types.Message, state: FSMContext):
    """Handle user's name input"""
    user_id = message.from_user.id
    name = message.text.strip()
    
    if len(name) > 50:
        await message.answer(
            "❌ **Name is too long!**\n\n"
            "Please keep it under 50 characters.\n"
            "Send /cancel to cancel.",
            parse_mode="Markdown"
        )
        return
    
    # Save name to database
    await user_db.update_user(user_id, display_name=name)
    await state.clear()
    
    await message.answer(
        f"✅ **Name saved successfully!**\n\n"
        f"📛 Your display name is now: `{name}`\n\n"
        f"Use /start to return to main menu.",
        parse_mode="Markdown"
    )


# ==================== HANDLE OWNER ID INPUT ====================
@router.message(StateFilter("waiting_for_owner_id"))
async def handle_owner_id_input(message: types.Message, state: FSMContext):
    """Handle user's owner ID input"""
    user_id = message.from_user.id
    owner_id_text = message.text.strip()
    
    # Validate if it's a number
    if not owner_id_text.isdigit():
        await message.answer(
            "❌ **Invalid Owner ID!**\n\n"
            "Owner ID must be a number.\n"
            "Example: `5661889723`\n\n"
            "Send /cancel to cancel.",
            parse_mode="Markdown"
        )
        return
    
    owner_id = int(owner_id_text)
    
    # Validate if it's a valid Telegram ID (basic check)
    if owner_id < 1 or owner_id > 9999999999:
        await message.answer(
            "❌ **Invalid Owner ID!**\n\n"
            "Please enter a valid Telegram User ID.\n"
            "Send /cancel to cancel.",
            parse_mode="Markdown"
        )
        return
    
    # Save owner ID to database
    await user_db.update_user(user_id, owner_id=owner_id)
    await state.clear()
    
    await message.answer(
        f"✅ **Owner ID saved successfully!**\n\n"
        f"🆔 Owner ID: `{owner_id}`\n\n"
        f"Use /start to return to main menu.",
        parse_mode="Markdown"
    )


# ==================== CANCEL ====================
@router.message(Command("cancel"))
async def cancel_cmd(message: types.Message, state: FSMContext):
    """Cancel current operation"""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer("❌ Nothing to cancel.")
        return
    
    await state.clear()
    
    await message.answer(
        "✅ **Cancelled!**\n\n"
        "Use /start to return to main menu.",
        parse_mode="Markdown"
    )


# ==================== MY BOTS ====================
@router.callback_query(F.data == "my_bots")
async def my_bots_callback(callback: CallbackQuery, state: FSMContext):
    """Show user's hosted bots"""
    await callback.answer()
    
    user_id = callback.from_user.id
    bots = await user_db.get_user_bots(user_id)
    
    if not bots:
        await callback.message.edit_text(
            "🤖 **My Bots**\n\n"
            "You don't have any bots hosted yet.\n\n"
            "📤 Use **Upload Tokens** to host your first bot!",
            parse_mode="Markdown"
        )
        return
    
    # Show bot list
    bot_text = "🤖 **My Bots**\n\n"
    for bot in bots:
        status_emoji = "🟢" if bot.get("status") == "running" else "🔴"
        bot_text += f"• {status_emoji} @{bot['bot_username']}\n"
        bot_text += f"  Status: `{bot.get('status', 'unknown')}`\n\n"
    
    bot_text += "\nUse /start to return to main menu."
    
    # Inline buttons for each bot
    keyboard = []
    for bot in bots:
        keyboard.append([
            InlineKeyboardButton(
                text=f"🤖 @{bot['bot_username']}",
                callback_data=f"bot_{bot['bot_username']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        bot_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ==================== UPLOAD TOKENS ====================
@router.callback_query(F.data == "upload_tokens")
async def upload_tokens_callback(callback: CallbackQuery, state: FSMContext):
    """Handle upload tokens button"""
    await callback.answer()
    await state.set_state("waiting_for_tokens")
    
    await callback.message.edit_text(
        "📤 **Upload Bot Tokens**\n\n"
        "Send me your bot tokens.\n"
        "📌 One token per line.\n"
        "📌 Maximum 10 tokens.\n\n"
        "**Example:**\n"
        "`1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`\n"
        "`0987654321:ZYXwvutsRQPonmLKJIhgfEDCBA`\n\n"
        "⚠️ Each token will create a separate bot.\n"
        "🔙 Send /cancel to cancel.",
        parse_mode="Markdown"
    )


# ==================== SUPPORT ====================
@router.callback_query(F.data == "support_menu")
async def support_callback(callback: CallbackQuery, state: FSMContext):
    """Show support menu"""
    await callback.answer()
    
    support_text = """🎫 **Contact Support**

Need help? Send a message below.

Our support team will get back to you.

━━━━━━━━━━━━━━━━━━━━━━━━━━

📢 **Channel:** @proxydominates
🆘 **Support:** @ncenginehost_bot

Powered By @proxydominates"""
    
    keyboard = [
        [InlineKeyboardButton(text="📩 Send Message", callback_data="send_support")],
        [InlineKeyboardButton(text="📢 Channel", url="https://t.me/proxydominates")],
        [InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        support_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ==================== SEND SUPPORT ====================
@router.callback_query(F.data == "send_support")
async def send_support_callback(callback: CallbackQuery, state: FSMContext):
    """Handle send support message"""
    await callback.answer()
    await state.set_state("waiting_for_support_message")
    
    await callback.message.edit_text(
        "📩 **Send Support Message**\n\n"
        "Write your message below.\n"
        "Our support team will reply soon.\n\n"
        "🔙 Send /cancel to cancel.",
        parse_mode="Markdown"
    )

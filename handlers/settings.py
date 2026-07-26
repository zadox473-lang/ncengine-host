# handlers/settings.py
# User Settings - Notifications, Language, Reset Profile

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from database.users import UserDB
from utils.logger import logger

router = Router()
user_db = UserDB()


# ==================== STATES ====================
class SettingsStates(StatesGroup):
    waiting_reset_confirm = State()


# ==================== SETTINGS MENU ====================
@router.callback_query(F.data == "settings_menu")
async def settings_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Show settings menu"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user_data = await user_db.get_user(user_id)
    
    if not user_data:
        await callback.message.edit_text(
            "❌ **User not found!**\n\n"
            "Please use /start first.",
            parse_mode="Markdown"
        )
        return
    
    # Get user settings
    notifications = user_data.get("notifications", True)
    language = user_data.get("language", "en")
    
    # Build settings text
    settings_text = (
        f"⚙️ **Settings**\n\n"
        f"🔔 **Notifications:** {'✅ ON' if notifications else '❌ OFF'}\n"
        f"🌐 **Language:** {language.upper()}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Customize your bot experience."
    )
    
    # Settings keyboard
    keyboard = [
        [
            InlineKeyboardButton(
                text=f"🔔 {'Turn Off' if notifications else 'Turn On'} Notifications",
                callback_data="toggle_notifications"
            )
        ],
        [
            InlineKeyboardButton(text="🌐 Language (Coming Soon)", callback_data="language_soon")
        ],
        [
            InlineKeyboardButton(text="🗑 Reset Profile", callback_data="reset_profile")
        ],
        [
            InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        settings_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ==================== TOGGLE NOTIFICATIONS ====================
@router.callback_query(F.data == "toggle_notifications")
async def toggle_notifications_callback(callback: CallbackQuery, state: FSMContext):
    """Toggle user notifications on/off"""
    await callback.answer()
    
    user_id = callback.from_user.id
    user_data = await user_db.get_user(user_id)
    
    if not user_data:
        await callback.message.edit_text(
            "❌ **User not found!**",
            parse_mode="Markdown"
        )
        return
    
    # Toggle notifications
    current = user_data.get("notifications", True)
    new_status = not current
    
    await user_db.update_user(user_id, notifications=new_status)
    
    # Refresh settings menu
    await settings_menu_callback(callback, state)
    
    logger.info(f"User {user_id} toggled notifications to: {new_status}")


# ==================== LANGUAGE (COMING SOON) ====================
@router.callback_query(F.data == "language_soon")
async def language_soon_callback(callback: CallbackQuery, state: FSMContext):
    """Show language feature coming soon message"""
    await callback.answer()
    
    await callback.message.edit_text(
        "🌐 **Language Settings**\n\n"
        "🛠 This feature is coming soon!\n\n"
        "Currently supported: **English**\n\n"
        "📌 More languages will be added in future updates.\n\n"
        "🔙 Click below to go back.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back to Settings", callback_data="settings_menu")]
        ])
    )


# ==================== RESET PROFILE ====================
@router.callback_query(F.data == "reset_profile")
async def reset_profile_callback(callback: CallbackQuery, state: FSMContext):
    """Ask for confirmation before resetting profile"""
    await callback.answer()
    await state.set_state(SettingsStates.waiting_reset_confirm)
    
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Yes, Reset Everything", callback_data="reset_confirm_yes"),
            InlineKeyboardButton(text="❌ Cancel", callback_data="settings_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        "⚠️ **⚠️ WARNING: Reset Profile ⚠️**\n\n"
        "Are you sure you want to reset your profile?\n\n"
        "This will permanently delete:\n"
        "❌ Your display name\n"
        "❌ Your owner ID\n"
        "❌ Your settings (notifications, language)\n"
        "❌ All your hosted bots (if any)\n\n"
        "**This action CANNOT be undone!**\n\n"
        "Type /cancel to abort.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ==================== RESET PROFILE CONFIRM ====================
@router.callback_query(F.data == "reset_confirm_yes")
async def reset_confirm_yes_callback(callback: CallbackQuery, state: FSMContext):
    """Confirm and reset user profile"""
    await callback.answer()
    
    user_id = callback.from_user.id
    
    # Reset user data in database
    await user_db.reset_user_profile(user_id)
    
    # Also delete all bots
    from database.bots import BotDB
    from services.deploy import deployer
    
    bot_db = BotDB()
    user_bots = await bot_db.get_user_bots(user_id)
    
    for bot in user_bots:
        await deployer.delete_bot(bot["bot_username"], user_id)
    
    await state.clear()
    
    await callback.message.edit_text(
        "🗑 **✅ Profile Reset Complete!**\n\n"
        "Your profile has been reset successfully.\n\n"
        "📌 What was deleted:\n"
        "✅ Display name removed\n"
        "✅ Owner ID removed\n"
        "✅ Settings reset to default\n"
        f"✅ {len(user_bots)} bot(s) deleted\n\n"
        "📝 To set up again:\n"
        "1. Set your name (Profile → Set Name)\n"
        "2. Set your owner ID (Profile → Set Owner ID)\n"
        "3. Upload tokens to host bots\n\n"
        "Use /start to return to main menu.",
        parse_mode="Markdown"
    )
    
    logger.info(f"User {user_id} reset their profile and deleted {len(user_bots)} bots")


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
        "Operation cancelled.\n"
        "Use /start to return to main menu.",
        parse_mode="Markdown"
    )


# ==================== SAVE USER SETTINGS ====================
@router.callback_query(F.data.startswith("set_lang_"))
async def set_language_callback(callback: CallbackQuery, state: FSMContext):
    """Set user language (future implementation)"""
    await callback.answer("🌐 Language feature coming soon!")
    
    # For future implementation:
    # lang = callback.data.replace("set_lang_", "")
    # await user_db.update_user(user_id, language=lang)

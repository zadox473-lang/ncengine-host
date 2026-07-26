# handlers/profile.py
# Profile management - View, Set Name, Set Owner ID

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from database.users import UserDB
from utils.logger import logger

router = Router()
user_db = UserDB()


# ==================== STATES ====================
class ProfileStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_owner_id = State()


# ==================== PROFILE MENU ====================
@router.callback_query(F.data == "profile_menu")
async def profile_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Show profile menu with user details"""
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
    
    # Get user details
    display_name = user_data.get("display_name", "Not Set")
    owner_id = user_data.get("owner_id", "Not Set")
    username = user_data.get("username", "NoUsername")
    first_name = user_data.get("first_name", "User")
    
    # Build profile text
    profile_text = (
        f"👤 **Your Profile**\n\n"
        f"📛 **Name:** `{display_name}`\n"
        f"🆔 **Owner ID:** `{owner_id}`\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"👤 **Username:** @{username}\n"
        f"📝 **First Name:** {first_name}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"What would you like to do?"
    )
    
    # Profile management keyboard
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
    await state.set_state(ProfileStates.waiting_for_name)
    
    await callback.message.edit_text(
        "📝 **Set Your Display Name**\n\n"
        "Send me your display name.\n"
        "This name will appear on your hosted bots.\n\n"
        "**Example:** `Asmit`\n\n"
        "📌 Max 50 characters.\n"
        "🔙 Send /cancel to cancel.",
        parse_mode="Markdown"
    )


# ==================== HANDLE NAME INPUT ====================
@router.message(ProfileStates.waiting_for_name)
async def handle_name_input(message: types.Message, state: FSMContext):
    """Handle user's name input"""
    user_id = message.from_user.id
    name = message.text.strip()
    
    # Validate name
    if not name:
        await message.answer(
            "❌ **Name cannot be empty!**\n\n"
            "Please send a valid name.\n"
            "🔙 Send /cancel to cancel.",
            parse_mode="Markdown"
        )
        return
    
    if len(name) > 50:
        await message.answer(
            "❌ **Name is too long!**\n\n"
            "Please keep it under 50 characters.\n"
            "🔙 Send /cancel to cancel.",
            parse_mode="Markdown"
        )
        return
    
    # Save name to database
    await user_db.update_user(user_id, display_name=name)
    await state.clear()
    
    # Get updated user data
    user_data = await user_db.get_user(user_id)
    
    await message.answer(
        f"✅ **Name saved successfully!**\n\n"
        f"📛 Your display name is now: `{name}`\n\n"
        f"👤 **Updated Profile:**\n"
        f"• Name: `{name}`\n"
        f"• Owner ID: `{user_data.get('owner_id', 'Not Set')}`\n\n"
        f"Use /start to return to main menu.",
        parse_mode="Markdown"
    )
    
    logger.info(f"User {user_id} set display name to: {name}")


# ==================== UNSET NAME ====================
@router.callback_query(F.data == "unset_name")
async def unset_name_callback(callback: CallbackQuery, state: FSMContext):
    """Unset user's display name"""
    await callback.answer()
    
    user_id = callback.from_user.id
    await user_db.update_user(user_id, display_name=None)
    
    await callback.message.edit_text(
        "✅ **Name has been removed!**\n\n"
        "Your profile name is now empty.\n\n"
        "🔄 Returning to profile...",
        parse_mode="Markdown"
    )
    
    # Go back to profile after 1 second
    await asyncio.sleep(1)
    await profile_menu_callback(callback, state)
    
    logger.info(f"User {user_id} removed display name")


# ==================== SET OWNER ID ====================
@router.callback_query(F.data == "set_owner_id")
async def set_owner_id_callback(callback: CallbackQuery, state: FSMContext):
    """Ask user for owner ID"""
    await callback.answer()
    await state.set_state(ProfileStates.waiting_for_owner_id)
    
    await callback.message.edit_text(
        "🆔 **Set Your Owner ID**\n\n"
        "Send me your Telegram User ID.\n"
        "This ID will be the owner of your hosted bots.\n\n"
        "**How to find your ID:**\n"
        "1. Send any message to @userinfobot\n"
        "2. Copy your ID\n\n"
        "**Example:** `5661889723`\n\n"
        "🔙 Send /cancel to cancel.",
        parse_mode="Markdown"
    )


# ==================== HANDLE OWNER ID INPUT ====================
@router.message(ProfileStates.waiting_for_owner_id)
async def handle_owner_id_input(message: types.Message, state: FSMContext):
    """Handle user's owner ID input"""
    user_id = message.from_user.id
    owner_id_text = message.text.strip()
    
    # Validate if it's a number
    if not owner_id_text.isdigit():
        await message.answer(
            "❌ **Invalid Owner ID!**\n\n"
            "Owner ID must be a number.\n"
            "**Example:** `5661889723`\n\n"
            "🔙 Send /cancel to cancel.",
            parse_mode="Markdown"
        )
        return
    
    owner_id = int(owner_id_text)
    
    # Basic validation for Telegram ID range
    if owner_id < 1 or owner_id > 9999999999:
        await message.answer(
            "❌ **Invalid Owner ID!**\n\n"
            "Please enter a valid Telegram User ID.\n"
            "🔙 Send /cancel to cancel.",
            parse_mode="Markdown"
        )
        return
    
    # Save owner ID to database
    await user_db.update_user(user_id, owner_id=owner_id)
    await state.clear()
    
    # Get updated user data
    user_data = await user_db.get_user(user_id)
    
    await message.answer(
        f"✅ **Owner ID saved successfully!**\n\n"
        f"🆔 Owner ID: `{owner_id}`\n\n"
        f"👤 **Updated Profile:**\n"
        f"• Name: `{user_data.get('display_name', 'Not Set')}`\n"
        f"• Owner ID: `{owner_id}`\n\n"
        f"Now you can host bots using **Upload Tokens**!\n\n"
        f"Use /start to return to main menu.",
        parse_mode="Markdown"
    )
    
    logger.info(f"User {user_id} set owner ID to: {owner_id}")


# ==================== UNSET OWNER ID ====================
@router.callback_query(F.data == "unset_owner_id")
async def unset_owner_id_callback(callback: CallbackQuery, state: FSMContext):
    """Unset user's owner ID"""
    await callback.answer()
    
    user_id = callback.from_user.id
    await user_db.update_user(user_id, owner_id=None)
    
    await callback.message.edit_text(
        "✅ **Owner ID has been removed!**\n\n"
        "Your bot owner ID is now empty.\n\n"
        "⚠️ You need to set Owner ID before hosting bots.\n\n"
        "🔄 Returning to profile...",
        parse_mode="Markdown"
    )
    
    # Go back to profile after 1 second
    await asyncio.sleep(1)
    await profile_menu_callback(callback, state)
    
    logger.info(f"User {user_id} removed owner ID")


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

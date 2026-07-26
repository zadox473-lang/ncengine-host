# handlers/mybots.py
# My Bots - List, manage and control hosted bots

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from database.users import UserDB
from database.bots import BotDB
from services.deploy import deployer
from utils.logger import logger

router = Router()
user_db = UserDB()
bot_db = BotDB()


# ==================== MY BOTS LIST ====================
@router.callback_query(F.data == "my_bots")
async def my_bots_callback(callback: CallbackQuery, state: FSMContext):
    """Show user's hosted bots list"""
    await callback.answer()
    
    user_id = callback.from_user.id
    bots = await bot_db.get_user_bots(user_id)
    
    if not bots:
        await callback.message.edit_text(
            "🤖 **My Bots**\n\n"
            "You don't have any bots hosted yet.\n\n"
            "📤 Use **Upload Tokens** to host your first bot!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📢 Channel: @proxydominates\n"
            "Powered By @proxydominates",
            parse_mode="Markdown"
        )
        return
    
    # Build bot list with status
    bot_text = "🤖 **My Bots**\n\n"
    bot_buttons = []
    
    for bot in bots:
        # Get real-time status
        status_data = await deployer.get_bot_status(bot["bot_username"])
        status = status_data.get("status", "stopped") if status_data.get("success") else "stopped"
        
        status_emoji = "🟢" if status == "running" else "🔴"
        status_text = "Running" if status == "running" else "Stopped"
        
        bot_text += f"{status_emoji} @{bot['bot_username']} - {status_text}\n"
        
        # Add button for each bot
        bot_buttons.append([
            InlineKeyboardButton(
                text=f"🤖 @{bot['bot_username']}",
                callback_data=f"bot_detail_{bot['bot_username']}"
            )
        ])
    
    # Add back button
    bot_buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="main_menu")])
    reply_markup = InlineKeyboardMarkup(inline_keyboard=bot_buttons)
    
    bot_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    bot_text += f"📊 Total: {len(bots)} bots\n"
    bot_text += "📢 Channel: @proxydominates\n"
    bot_text += "Powered By @proxydominates"
    
    await callback.message.edit_text(
        bot_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ==================== BOT DETAIL VIEW ====================
@router.callback_query(F.data.startswith("bot_detail_"))
async def bot_detail_callback(callback: CallbackQuery, state: FSMContext):
    """Show individual bot details with management options"""
    await callback.answer()
    
    bot_username = callback.data.replace("bot_detail_", "")
    user_id = callback.from_user.id
    
    # Get bot details
    bot_data = await bot_db.get_bot_by_username(bot_username)
    if not bot_data:
        await callback.message.edit_text(
            "❌ **Bot not found!**\n\n"
            "This bot no longer exists.",
            parse_mode="Markdown"
        )
        return
    
    # Check if user owns this bot
    if bot_data["user_id"] != user_id:
        await callback.message.edit_text(
            "❌ **Unauthorized!**\n\n"
            "You don't own this bot.",
            parse_mode="Markdown"
        )
        return
    
    # Get real-time status
    status_data = await deployer.get_bot_status(bot_username)
    status = status_data.get("status", "stopped") if status_data.get("success") else "stopped"
    pid = status_data.get("pid") if status_data.get("success") else None
    
    status_emoji = "🟢" if status == "running" else "🔴"
    status_text = "Running" if status == "running" else "Stopped"
    
    # Build detail text
    detail_text = (
        f"🤖 **@{bot_username}**\n\n"
        f"📊 **Status:** {status_emoji} {status_text}\n"
        f"🆔 **Bot ID:** `{bot_data.get('bot_id', 'N/A')}`\n"
        f"📅 **Created:** {bot_data.get('created_at', 'N/A')}\n"
        f"👤 **Owner:** {bot_data.get('display_name', 'Unknown')}\n"
    )
    
    if pid:
        detail_text += f"🔢 **PID:** `{pid}`\n"
    
    detail_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    detail_text += "📢 Channel: @proxydominates\n"
    detail_text += "Powered By @proxydominates"
    
    # Management buttons
    keyboard = []
    
    if status == "running":
        keyboard.append([
            InlineKeyboardButton(text="⏹ Stop", callback_data=f"bot_stop_{bot_username}"),
            InlineKeyboardButton(text="🔄 Restart", callback_data=f"bot_restart_{bot_username}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(text="▶️ Start", callback_data=f"bot_start_{bot_username}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🗑 Delete", callback_data=f"bot_delete_{bot_username}")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🔙 Back to List", callback_data="my_bots"),
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    ])
    
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        detail_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ==================== START BOT ====================
@router.callback_query(F.data.startswith("bot_start_"))
async def bot_start_callback(callback: CallbackQuery, state: FSMContext):
    """Start a hosted bot"""
    await callback.answer()
    
    bot_username = callback.data.replace("bot_start_", "")
    user_id = callback.from_user.id
    
    # Verify ownership
    bot_data = await bot_db.get_bot_by_username(bot_username)
    if not bot_data or bot_data["user_id"] != user_id:
        await callback.message.edit_text("❌ Unauthorized!")
        return
    
    # Start the bot
    result = await deployer.start_bot(bot_username)
    
    if result.get("success"):
        await callback.message.edit_text(
            f"✅ **Bot @{bot_username} started successfully!**\n\n"
            f"Status: 🟢 Running\n\n"
            f"⏳ Refreshing...",
            parse_mode="Markdown"
        )
        # Wait a moment then refresh
        await asyncio.sleep(1)
        await bot_detail_callback(callback, state)
    else:
        await callback.message.edit_text(
            f"❌ **Failed to start @{bot_username}**\n\n"
            f"Error: {result.get('error', 'Unknown error')}",
            parse_mode="Markdown"
        )


# ==================== STOP BOT ====================
@router.callback_query(F.data.startswith("bot_stop_"))
async def bot_stop_callback(callback: CallbackQuery, state: FSMContext):
    """Stop a running bot"""
    await callback.answer()
    
    bot_username = callback.data.replace("bot_stop_", "")
    user_id = callback.from_user.id
    
    # Verify ownership
    bot_data = await bot_db.get_bot_by_username(bot_username)
    if not bot_data or bot_data["user_id"] != user_id:
        await callback.message.edit_text("❌ Unauthorized!")
        return
    
    # Stop the bot
    result = await deployer.stop_bot(bot_username)
    
    if result.get("success"):
        await callback.message.edit_text(
            f"✅ **Bot @{bot_username} stopped successfully!**\n\n"
            f"Status: 🔴 Stopped\n\n"
            f"⏳ Refreshing...",
            parse_mode="Markdown"
        )
        # Wait a moment then refresh
        await asyncio.sleep(1)
        await bot_detail_callback(callback, state)
    else:
        await callback.message.edit_text(
            f"❌ **Failed to stop @{bot_username}**\n\n"
            f"Error: {result.get('error', 'Unknown error')}",
            parse_mode="Markdown"
        )


# ==================== RESTART BOT ====================
@router.callback_query(F.data.startswith("bot_restart_"))
async def bot_restart_callback(callback: CallbackQuery, state: FSMContext):
    """Restart a bot"""
    await callback.answer()
    
    bot_username = callback.data.replace("bot_restart_", "")
    user_id = callback.from_user.id
    
    # Verify ownership
    bot_data = await bot_db.get_bot_by_username(bot_username)
    if not bot_data or bot_data["user_id"] != user_id:
        await callback.message.edit_text("❌ Unauthorized!")
        return
    
    # Restart the bot
    result = await deployer.restart_bot(bot_username)
    
    if result.get("success"):
        await callback.message.edit_text(
            f"✅ **Bot @{bot_username} restarted successfully!**\n\n"
            f"Status: 🟢 Running\n\n"
            f"⏳ Refreshing...",
            parse_mode="Markdown"
        )
        # Wait a moment then refresh
        await asyncio.sleep(1)
        await bot_detail_callback(callback, state)
    else:
        await callback.message.edit_text(
            f"❌ **Failed to restart @{bot_username}**\n\n"
            f"Error: {result.get('error', 'Unknown error')}",
            parse_mode="Markdown"
        )


# ==================== DELETE BOT ====================
@router.callback_query(F.data.startswith("bot_delete_"))
async def bot_delete_callback(callback: CallbackQuery, state: FSMContext):
    """Delete a bot (with confirmation)"""
    await callback.answer()
    
    bot_username = callback.data.replace("bot_delete_", "")
    user_id = callback.from_user.id
    
    # Verify ownership
    bot_data = await bot_db.get_bot_by_username(bot_username)
    if not bot_data or bot_data["user_id"] != user_id:
        await callback.message.edit_text("❌ Unauthorized!")
        return
    
    # Ask for confirmation
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Yes, Delete", callback_data=f"bot_delete_confirm_{bot_username}"),
            InlineKeyboardButton(text="❌ Cancel", callback_data=f"bot_detail_{bot_username}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await callback.message.edit_text(
        f"⚠️ **Delete Bot @{bot_username}**\n\n"
        f"Are you sure you want to delete this bot?\n\n"
        f"This action **cannot be undone**!\n\n"
        f"All bot data and files will be removed.",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )


# ==================== DELETE BOT CONFIRM ====================
@router.callback_query(F.data.startswith("bot_delete_confirm_"))
async def bot_delete_confirm_callback(callback: CallbackQuery, state: FSMContext):
    """Confirm and delete bot"""
    await callback.answer()
    
    bot_username = callback.data.replace("bot_delete_confirm_", "")
    user_id = callback.from_user.id
    
    # Verify ownership
    bot_data = await bot_db.get_bot_by_username(bot_username)
    if not bot_data or bot_data["user_id"] != user_id:
        await callback.message.edit_text("❌ Unauthorized!")
        return
    
    # Delete the bot
    result = await deployer.delete_bot(bot_username, user_id)
    
    if result.get("success"):
        await callback.message.edit_text(
            f"🗑 **Bot @{bot_username} deleted successfully!**\n\n"
            f"All data has been removed.\n\n"
            f"🔄 Returning to bot list...",
            parse_mode="Markdown"
        )
        # Wait then go back to list
        await asyncio.sleep(1)
        await my_bots_callback(callback, state)
    else:
        await callback.message.edit_text(
            f"❌ **Failed to delete @{bot_username}**\n\n"
            f"Error: {result.get('error', 'Unknown error')}",
            parse_mode="Markdown"
        )


# ==================== REFRESH BOT STATUS ====================
@router.callback_query(F.data.startswith("bot_refresh_"))
async def bot_refresh_callback(callback: CallbackQuery, state: FSMContext):
    """Refresh bot status"""
    await callback.answer("🔄 Refreshing...")
    bot_username = callback.data.replace("bot_refresh_", "")
    await bot_detail_callback(callback, state)

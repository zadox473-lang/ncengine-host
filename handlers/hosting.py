# handlers/host.py
# Token upload, validation and bot deployment handler for NC ENGINE HOST

from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.users import UserDB
from database.bots import BotDB
from services.deploy import deployer
from utils.validators import validate_bot_token, get_bot_info
from utils.logger import logger

router = Router()
user_db = UserDB()
bot_db = BotDB()

# ==================== STATES ====================
class HostStates(StatesGroup):
    waiting_for_tokens = State()


# ==================== UPLOAD TOKENS ====================
@router.callback_query(F.data == "upload_tokens")
async def upload_tokens_callback(callback: types.CallbackQuery, state: FSMContext):
    """Handle upload tokens button - ask user for tokens"""
    await callback.answer()
    await state.set_state(HostStates.waiting_for_tokens)
    
    # Check if user has name and owner ID set
    user_id = callback.from_user.id
    user_data = await user_db.get_user(user_id)
    
    if not user_data:
        await callback.message.edit_text(
            "❌ **Error: User not found!**\n\n"
            "Please use /start first.",
            parse_mode="Markdown"
        )
        return
    
    # Check if display name is set
    if not user_data.get("display_name"):
        await callback.message.edit_text(
            "❌ **Display Name Not Set!**\n\n"
            "Please set your display name first.\n"
            "Go to **Profile → Set Name**\n\n"
            "🔙 Use /start to return.",
            parse_mode="Markdown"
        )
        return
    
    # Check if owner ID is set
    if not user_data.get("owner_id"):
        await callback.message.edit_text(
            "❌ **Owner ID Not Set!**\n\n"
            "Please set your owner ID first.\n"
            "Go to **Profile → Set Owner ID**\n\n"
            "🔙 Use /start to return.",
            parse_mode="Markdown"
        )
        return
    
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


# ==================== HANDLE TOKENS INPUT ====================
@router.message(HostStates.waiting_for_tokens)
async def handle_tokens_input(message: types.Message, state: FSMContext):
    """Handle user's token input - validate and deploy"""
    user_id = message.from_user.id
    token_text = message.text.strip()
    
    # Parse tokens (one per line)
    tokens = [t.strip() for t in token_text.split('\n') if t.strip()]
    
    # Check if any tokens provided
    if not tokens:
        await message.answer(
            "❌ **No tokens found!**\n\n"
            "Please send valid bot tokens.\n"
            "One token per line.\n\n"
            "🔙 Send /cancel to cancel.",
            parse_mode="Markdown"
        )
        return
    
    # Limit to 10 tokens
    if len(tokens) > 10:
        await message.answer(
            f"❌ **Too many tokens!**\n\n"
            f"You sent {len(tokens)} tokens.\n"
            f"Maximum allowed: **10** tokens.\n\n"
            f"Please send only 10 tokens.\n"
            f"🔙 Send /cancel to cancel.",
            parse_mode="Markdown"
        )
        return
    
    # Clear state
    await state.clear()
    
    # Send processing message
    processing_msg = await message.answer(
        f"⏳ **Processing {len(tokens)} tokens...**\n\n"
        f"Please wait while I validate and deploy your bots.",
        parse_mode="Markdown"
    )
    
    # Get user data
    user_data = await user_db.get_user(user_id)
    display_name = user_data.get("display_name", "User")
    owner_id = user_data.get("owner_id", user_id)
    
    # Validate each token
    valid_tokens = []
    invalid_tokens = []
    duplicate_tokens = []
    
    for token in tokens:
        # Check if token already exists in system
        existing_bot = await bot_db.get_bot_by_token(token)
        if existing_bot:
            duplicate_tokens.append(token)
            continue
        
        # Validate token format
        if not validate_bot_token(token):
            invalid_tokens.append({"token": token, "reason": "Invalid format"})
            continue
        
        # Check if token is valid with Telegram API
        bot_info = await get_bot_info(token)
        if not bot_info:
            invalid_tokens.append({"token": token, "reason": "Invalid token (API check failed)"})
            continue
        
        valid_tokens.append({"token": token, "bot_info": bot_info})
    
    # Check if user has reached max bots limit
    user_bots = await bot_db.get_user_bots(user_id)
    if len(user_bots) + len(valid_tokens) > 10:
        remaining = 10 - len(user_bots)
        await processing_msg.edit_text(
            f"❌ **Bot Limit Reached!**\n\n"
            f"You already have {len(user_bots)} bots.\n"
            f"You can only have **10** bots total.\n"
            f"You can add {remaining} more bots.\n\n"
            f"Please remove some bots first.",
            parse_mode="Markdown"
        )
        return
    
    # Deploy valid tokens
    deployed = []
    failed = []
    
    for item in valid_tokens:
        token = item["token"]
        bot_info = item["bot_info"]
        bot_username = bot_info.get("username")
        
        # Deploy bot
        result = await deployer.deploy_bot(
            user_id=user_id,
            bot_token=token,
            owner_id=owner_id,
            display_name=display_name,
            bot_username=bot_username
        )
        
        if result.get("success"):
            deployed.append(bot_username)
        else:
            failed.append({"token": token, "reason": result.get("error", "Unknown error")})
    
    # Build response message
    response_text = ""
    
    if deployed:
        response_text += f"✅ **{len(deployed)} bot(s) deployed successfully!**\n\n"
        for username in deployed:
            response_text += f"🤖 @{username}\n"
        response_text += "\n"
    
    if failed:
        response_text += f"❌ **{len(failed)} bot(s) failed:**\n\n"
        for item in failed:
            response_text += f"• `{item['token'][:15]}...` - {item['reason']}\n"
        response_text += "\n"
    
    if invalid_tokens:
        response_text += f"❌ **Invalid tokens ({len(invalid_tokens)}):**\n\n"
        for item in invalid_tokens:
            response_text += f"• `{item['token'][:15]}...` - {item['reason']}\n"
        response_text += "\n"
    
    if duplicate_tokens:
        response_text += f"⚠️ **Duplicate tokens ({len(duplicate_tokens)}):**\n\n"
        for token in duplicate_tokens:
            response_text += f"• `{token[:15]}...` - Already hosted\n"
        response_text += "\n"
    
    if not deployed and not failed and not invalid_tokens and not duplicate_tokens:
        response_text = "❌ **No tokens processed!**\n\nPlease send valid tokens."
    
    # Add footer
    response_text += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    response_text += "📊 Use /mybots to see your bots.\n"
    response_text += "📢 Channel: @proxydominates\n"
    response_text += f"Powered By @proxydominates"
    
    await processing_msg.edit_text(
        response_text,
        parse_mode="Markdown"
    )
    
    # Notify owner if bots deployed
    if deployed:
        await notify_owner(user_id, deployed, display_name, len(deployed))
    
    logger.info(f"User {user_id} deployed {len(deployed)} bots")


# ==================== NOTIFY OWNER ====================
async def notify_owner(user_id: int, deployed_bots: list, display_name: str, count: int):
    """Notify the main owner about new bot deployment"""
    from config import OWNER_ID
    from main import bot
    
    user_data = await user_db.get_user(user_id)
    username = user_data.get("username", "NoUsername") if user_data else "NoUsername"
    
    bot_list = "\n".join([f"🤖 @{b}" for b in deployed_bots])
    
    notification_text = (
        f"🚀 **New Bots Deployed!**\n\n"
        f"👤 **User:** {display_name}\n"
        f"🆔 **User ID:** `{user_id}`\n"
        f"👤 **Username:** @{username}\n"
        f"📦 **Bots:** {count}\n\n"
        f"{bot_list}\n\n"
        f"⏰ **Time:** {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"🔗 **View User:** /view_user_{user_id}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 View User", callback_data=f"view_user_{user_id}")]
    ])
    
    try:
        await bot.send_message(
            chat_id=OWNER_ID,
            text=notification_text,
            parse_mode="Markdown",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")


# ==================== CANCEL ====================
@router.message(Command("cancel"))
async def cancel_cmd(message: types.Message, state: FSMContext):
    """Cancel token upload"""
    current_state = await state.get_state()
    
    if current_state != HostStates.waiting_for_tokens:
        await message.answer("❌ Nothing to cancel.")
        return
    
    await state.clear()
    
    await message.answer(
        "✅ **Cancelled!**\n\n"
        "Token upload cancelled.\n"
        "Use /start to return.",
        parse_mode="Markdown"
                                 )

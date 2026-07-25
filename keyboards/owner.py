from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def owner_panel():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="📊 Statistics",
                    callback_data="owner_stats"
                )
            ],

            [
                InlineKeyboardButton(
                    text="👥 Users",
                    callback_data="owner_users"
                ),
                InlineKeyboardButton(
                    text="🤖 Hosted Bots",
                    callback_data="owner_bots"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🎫 Tickets",
                    callback_data="owner_tickets"
                ),
                InlineKeyboardButton(
                    text="📢 Broadcast",
                    callback_data="owner_broadcast"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🔍 Search User",
                    callback_data="owner_search"
                )
            ]
        ]
    )


def bot_control(bot_id: int):

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="▶️ Start",
                    callback_data=f"startbot:{bot_id}"
                ),
                InlineKeyboardButton(
                    text="⏹️ Stop",
                    callback_data=f"stopbot:{bot_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🔄 Restart",
                    callback_data=f"restartbot:{bot_id}"
                ),
                InlineKeyboardButton(
                    text="📄 Logs",
                    callback_data=f"logs:{bot_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="❌ Delete",
                    callback_data=f"deletebot:{bot_id}"
                )
            ]
        ]
    )


def ticket_control(ticket_id: str):

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="💬 Reply",
                    callback_data=f"reply:{ticket_id}"
                )
            ],

            [
                InlineKeyboardButton(
                    text="✅ Close",
                    callback_data=f"close:{ticket_id}"
                )
            ]
        ]
    )

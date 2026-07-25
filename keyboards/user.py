from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def start_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="🤖 Host Bots",
                    callback_data="host_bots"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📂 My Hosting",
                    callback_data="my_hosting"
                ),
                InlineKeyboardButton(
                    text="⚙️ Settings",
                    callback_data="settings"
                )
            ],

            [
                InlineKeyboardButton(
                    text="💬 Support",
                    url="https://t.me/noruleclub"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📢 Channel",
                    url="https://t.me/proxydominates"
                ),
                InlineKeyboardButton(
                    text="ℹ️ About",
                    callback_data="about"
                )
            ]

        ]
    )


def settings_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="👤 Set Name",
                    callback_data="set_name"
                )
            ],

            [
                InlineKeyboardButton(
                    text="🆔 Set Owner ID",
                    callback_data="set_owner"
                )
            ],

            [
                InlineKeyboardButton(
                    text="❌ Remove Name",
                    callback_data="remove_name"
                ),
                InlineKeyboardButton(
                    text="❌ Remove Owner ID",
                    callback_data="remove_owner"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data="back_home"
                )
            ]

        ]
    )


def hosting_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="➕ Upload 10 Tokens",
                    callback_data="upload_tokens"
                )
            ],

            [
                InlineKeyboardButton(
                    text="📊 My Bots",
                    callback_data="my_bots"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data="back_home"
                )
            ]

        ]
    )


def support_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="✍️ Create Ticket",
                    callback_data="create_ticket"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data="back_home"
                )
            ]

        ]
    )


def about_keyboard():

    return InlineKeyboardMarkup(
        inline_keyboard=[

            [
                InlineKeyboardButton(
                    text="📢 Channel",
                    url="https://t.me/proxydominates"
                )
            ],

            [
                InlineKeyboardButton(
                    text="💬 Support",
                    url="https://t.me/noruleclub"
                )
            ],

            [
                InlineKeyboardButton(
                    text="⬅️ Back",
                    callback_data="back_home"
                )
            ]

        ]
    )

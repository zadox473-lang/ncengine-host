from database.connection import execute, fetch, fetchrow, fetchval


async def add_bot(
    user_id: int,
    bot_id: int,
    bot_name: str,
    bot_username: str,
    bot_token: str,
    process_name: str,
):
    """
    Save hosted bot.
    """

    await execute(
        """
        INSERT INTO bots (
            user_id,
            bot_id,
            bot_name,
            bot_username,
            bot_token,
            process_name
        )

        VALUES ($1,$2,$3,$4,$5,$6)

        ON CONFLICT (bot_token)
        DO NOTHING
        """,
        user_id,
        bot_id,
        bot_name,
        bot_username,
        bot_token,
        process_name,
    )


async def token_exists(bot_token: str):
    """
    Check duplicate token.
    """

    return await fetchval(
        """
        SELECT EXISTS(
            SELECT 1
            FROM bots
            WHERE bot_token=$1
        )
        """,
        bot_token,
    )


async def get_bot(bot_id: int):
    """
    Get single bot.
    """

    return await fetchrow(
        """
        SELECT *
        FROM bots
        WHERE bot_id=$1
        """,
        bot_id,
    )


async def get_user_bots(user_id: int):
    """
    Get all bots of user.
    """

    return await fetch(
        """
        SELECT *
        FROM bots
        WHERE user_id=$1
        ORDER BY hosted_at DESC
        """,
        user_id,
    )


async def get_all_bots():
    """
    Owner panel.
    """

    return await fetch(
        """
        SELECT *
        FROM bots
        ORDER BY hosted_at DESC
        """
    )


async def update_status(
    bot_id: int,
    status: str,
):
    """
    running / stopped
    """

    await execute(
        """
        UPDATE bots
        SET status=$1
        WHERE bot_id=$2
        """,
        status,
        bot_id,
    )


async def update_process(
    bot_id: int,
    process_name: str,
):
    """
    Update process.
    """

    await execute(
        """
        UPDATE bots
        SET process_name=$1
        WHERE bot_id=$2
        """,
        process_name,
        bot_id,
    )


async def delete_bot(bot_id: int):
    """
    Delete bot.
    """

    await execute(
        """
        DELETE FROM bots
        WHERE bot_id=$1
        """,
        bot_id,
    )


async def delete_user_bots(user_id: int):
    """
    Delete all bots of user.
    """

    await execute(
        """
        DELETE FROM bots
        WHERE user_id=$1
        """,
        user_id,
    )


async def total_bots():
    """
    Total hosted bots.
    """

    return await fetchval(
        """
        SELECT COUNT(*)
        FROM bots
        """
    )


async def running_bots():
    """
    Running bots.
    """

    return await fetchval(
        """
        SELECT COUNT(*)
        FROM bots
        WHERE status='running'
        """
    )


async def stopped_bots():
    """
    Stopped bots.
    """

    return await fetchval(
        """
        SELECT COUNT(*)
        FROM bots
        WHERE status='stopped'
        """
    )

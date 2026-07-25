from database.connection import execute, fetchrow, fetch


async def register_user(
    user_id: int,
    username: str | None,
    first_name: str | None
):
    """
    Register user if not exists.
    """

    await execute(
        """
        INSERT INTO users (
            user_id,
            username,
            first_name
        )

        VALUES ($1,$2,$3)

        ON CONFLICT (user_id)
        DO NOTHING
        """,
        user_id,
        username,
        first_name
    )


async def get_user(user_id: int):
    """
    Get single user.
    """

    return await fetchrow(
        """
        SELECT *
        FROM users
        WHERE user_id=$1
        """,
        user_id
    )


async def get_all_users():
    """
    Get all users.
    """

    return await fetch(
        """
        SELECT *
        FROM users
        ORDER BY created_at DESC
        """
    )


async def update_display_name(
    user_id: int,
    display_name: str
):
    """
    Set display name.
    """

    await execute(
        """
        UPDATE users
        SET
            display_name=$1,
            updated_at=NOW()
        WHERE user_id=$2
        """,
        display_name,
        user_id
    )


async def update_owner_id(
    user_id: int,
    owner_id: int
):
    """
    Set owner id.
    """

    await execute(
        """
        UPDATE users
        SET
            owner_id=$1,
            updated_at=NOW()
        WHERE user_id=$2
        """,
        owner_id,
        user_id
    )


async def remove_owner_id(user_id: int):
    """
    Remove owner id.
    """

    await execute(
        """
        UPDATE users
        SET
            owner_id=NULL,
            updated_at=NOW()
        WHERE user_id=$1
        """,
        user_id
    )


async def increase_hosted_count(
    user_id: int,
    amount: int = 1
):
    """
    Increase hosted bots count.
    """

    await execute(
        """
        UPDATE users
        SET
            hosted_count=hosted_count+$1,
            updated_at=NOW()
        WHERE user_id=$2
        """,
        amount,
        user_id
    )


async def decrease_hosted_count(
    user_id: int,
    amount: int = 1
):
    """
    Decrease hosted bots count.
    """

    await execute(
        """
        UPDATE users
        SET
            hosted_count=GREATEST(hosted_count-$1,0),
            updated_at=NOW()
        WHERE user_id=$2
        """,
        amount,
        user_id
    )


async def ban_user(user_id: int):
    """
    Ban user.
    """

    await execute(
        """
        UPDATE users
        SET is_banned=TRUE
        WHERE user_id=$1
        """,
        user_id
    )


async def unban_user(user_id: int):
    """
    Unban user.
    """

    await execute(
        """
        UPDATE users
        SET is_banned=FALSE
        WHERE user_id=$1
        """,
        user_id
    )
async def remove_display_name(user_id: int):
    """
    Remove display name.
    """

    await execute(
        """
        UPDATE users
        SET
            display_name='User',
            updated_at=NOW()
        WHERE user_id=$1
        """,
        user_id
    )

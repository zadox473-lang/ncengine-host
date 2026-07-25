from database.connection import execute, fetch, fetchrow, fetchval
import uuid


async def create_ticket(user_id: int):
    """
    Create new support ticket.
    """

    ticket_id = str(uuid.uuid4())[:8].upper()

    await execute(
        """
        INSERT INTO tickets (
            ticket_id,
            user_id,
            status
        )

        VALUES ($1,$2,'open')
        """,
        ticket_id,
        user_id,
    )

    return ticket_id


async def get_ticket(ticket_id: str):
    """
    Get ticket by id.
    """

    return await fetchrow(
        """
        SELECT *
        FROM tickets
        WHERE ticket_id=$1
        """,
        ticket_id,
    )


async def get_user_ticket(user_id: int):
    """
    Get latest ticket of user.
    """

    return await fetchrow(
        """
        SELECT *
        FROM tickets
        WHERE user_id=$1
        ORDER BY created_at DESC
        LIMIT 1
        """,
        user_id,
    )


async def get_open_tickets():
    """
    Get all open tickets.
    """

    return await fetch(
        """
        SELECT *
        FROM tickets
        WHERE status='open'
        ORDER BY created_at DESC
        """
    )


async def get_closed_tickets():
    """
    Get all closed tickets.
    """

    return await fetch(
        """
        SELECT *
        FROM tickets
        WHERE status='closed'
        ORDER BY created_at DESC
        """
    )


async def close_ticket(ticket_id: str):
    """
    Close support ticket.
    """

    await execute(
        """
        UPDATE tickets
        SET status='closed'
        WHERE ticket_id=$1
        """,
        ticket_id,
    )


async def reopen_ticket(ticket_id: str):
    """
    Reopen support ticket.
    """

    await execute(
        """
        UPDATE tickets
        SET status='open'
        WHERE ticket_id=$1
        """,
        ticket_id,
    )


async def delete_ticket(ticket_id: str):
    """
    Delete ticket.
    """

    await execute(
        """
        DELETE FROM tickets
        WHERE ticket_id=$1
        """,
        ticket_id,
    )


async def total_tickets():
    """
    Total tickets.
    """

    return await fetchval(
        """
        SELECT COUNT(*)
        FROM tickets
        """
    )


async def total_open_tickets():
    """
    Open tickets count.
    """

    return await fetchval(
        """
        SELECT COUNT(*)
        FROM tickets
        WHERE status='open'
        """
    )


async def total_closed_tickets():
    """
    Closed tickets count.
    """

    return await fetchval(
        """
        SELECT COUNT(*)
        FROM tickets
        WHERE status='closed'
        """
    )

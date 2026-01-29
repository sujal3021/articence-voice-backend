# app/crud.py
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Call, CallStatus


async def get_or_create_call(session: AsyncSession, call_id: str) -> Call:
    """Get existing call or create a new one if it doesn't exist."""
    stmt = select(Call).where(Call.call_id == call_id)
    result = await session.execute(stmt)
    call = result.scalar_one_or_none()

    if call is None:
        call = Call(call_id=call_id)
        session.add(call)
        await session.commit()
        await session.refresh(call)
    
    return call


async def update_packet_info(
    session: AsyncSession,
    call_id: str,
    sequence: int,
    increment_count: bool = True
) -> None:
    """
    Update last_sequence and optionally increment packet_count.
    Only updates if the new sequence is higher (handles out-of-order packets).
    """
    stmt = (
        update(Call)
        .where(Call.call_id == call_id)
        .where(Call.last_sequence < sequence)  # only update if newer
        .values(last_sequence=sequence)
    )
    if increment_count:
        stmt = stmt.values(packet_count=Call.packet_count + 1)

    await session.execute(stmt)
    await session.commit()


async def update_call_status(
    session: AsyncSession,
    call_id: str,
    status: CallStatus
) -> None:
    """Update the status of a call."""
    stmt = (
        update(Call)
        .where(Call.call_id == call_id)
        .values(status=status)
    )
    await session.execute(stmt)
    await session.commit()


async def save_ai_results(
    session: AsyncSession,
    call_id: str,
    transcription: str | None,
    sentiment: str | None
) -> None:
    """Save transcription and sentiment results after AI processing."""
    stmt = (
        update(Call)
        .where(Call.call_id == call_id)
        .values(
            transcription=transcription,
            sentiment=sentiment,
            status=CallStatus.COMPLETED
        )
    )
    await session.execute(stmt)
    await session.commit()


async def get_call_by_id(session: AsyncSession, call_id: str) -> Call | None:
    """Retrieve a call by ID for debugging or dashboard."""
    stmt = select(Call).where(Call.call_id == call_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()
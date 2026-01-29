# app/routers/call.py
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..dependencies import get_db
from ..schemas import AudioPacket
from ..crud import (
    get_or_create_call,
    update_packet_info,
    update_call_status,
    save_ai_results
)
from ..models import CallStatus
from ..services.ai_service import mock_transcribe_and_analyze, AIServiceError

router = APIRouter(prefix="/v1/call", tags=["calls"])

logger = logging.getLogger(__name__)


async def process_call_in_background(
    call_id: str,
    session: AsyncSession,
    collected_packets: list[str]
):
    """Background task: run AI transcription & sentiment on collected packets."""
    try:
        await update_call_status(session, call_id, CallStatus.PROCESSING_AI)
        logger.info(f"Starting AI processing for call {call_id}")

        transcription, sentiment = await mock_transcribe_and_analyze(collected_packets)

        await save_ai_results(session, call_id, transcription, sentiment)
        logger.info(f"AI processing completed for call {call_id}: sentiment={sentiment}")

    except AIServiceError as e:
        logger.error(f"AI service failed after retries for {call_id}: {e}")
        await update_call_status(session, call_id, CallStatus.FAILED)
    except Exception as e:
        logger.exception(f"Unexpected error in AI background task for {call_id}")
        await update_call_status(session, call_id, CallStatus.FAILED)


@router.post("/stream/{call_id}", status_code=status.HTTP_202_ACCEPTED)
async def ingest_audio_packet(
    call_id: str,
    packet: AudioPacket,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db)
):
    """
    Ingest one audio metadata packet for a call.
    - Non-blocking: returns 202 immediately
    - Logs warnings for out-of-order or duplicate packets
    - Triggers AI processing in background when packet_count >= threshold
    """
    # Get or create call record
    call = await get_or_create_call(session, call_id)

    # Log sequence issues but never block
    if packet.sequence <= call.last_sequence:
        logger.warning(
            f"Out-of-order or duplicate packet: call={call_id}, "
            f"seq={packet.sequence}, last_seen={call.last_sequence}"
        )
    elif packet.sequence > call.last_sequence + 1:
        logger.warning(
            f"Missing packets detected: call={call_id}, "
            f"expected={call.last_sequence + 1}, received={packet.sequence}"
        )

    # Update sequence and count (only if newer sequence)
    await update_packet_info(
        session,
        call_id=call_id,
        sequence=packet.sequence,
        increment_count=True
    )

    # Dummy trigger condition: start AI after 10 packets (replace with real logic later)
    # In production: use timeout, explicit /complete endpoint, or WebSocket end signal
    if call.packet_count + 1 >= 10:  # +1 because we just incremented
        # For demo: collect dummy packets (in real: store actual data in DB/Redis)
        dummy_packets = ["dummy_audio_chunk"] * call.packet_count
        background_tasks.add_task(
            process_call_in_background,
            call_id=call_id,
            session=session,
            collected_packets=dummy_packets
        )
        logger.info(f"Queued AI processing for call {call_id} in background")

    return {"status": "accepted", "call_id": call_id, "sequence": packet.sequence}
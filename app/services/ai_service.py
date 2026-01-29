# app/services/ai_service.py
import asyncio
import random
from typing import Tuple

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    after_log,
    retry_if_result
)

import logging

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised when the mock AI service fails (simulating 503)."""
    pass


def is_transient_error(exception: Exception) -> bool:
    """Custom retry condition for transient failures."""
    return isinstance(exception, AIServiceError)


@retry(
    retry=retry_if_exception_type(AIServiceError),
    stop=stop_after_attempt(5),                     # max 5 attempts
    wait=wait_exponential(multiplier=1, min=1, max=10),  # 1s → 2s → 4s → 8s → 10s
    before_sleep=before_sleep_log(logger, logging.WARNING),
    after=after_log(logger, logging.INFO),
    reraise=True
)
async def mock_transcribe_and_analyze(packets: list[str]) -> Tuple[str, str]:
    """
    Mock external AI service: transcription + sentiment analysis.
    
    - 25% chance to fail (raise AIServiceError)
    - 1–3 seconds random latency
    - Returns dummy transcription and sentiment
    """
    # Simulate 25% failure rate
    if random.random() < 0.25:
        logger.warning("Mock AI service failed (simulating 503)")
        raise AIServiceError("AI service temporarily unavailable (503)")

    # Simulate variable latency (1–3 seconds)
    delay = random.uniform(1.0, 3.0)
    logger.info(f"Mock AI processing... waiting {delay:.2f} seconds")
    await asyncio.sleep(delay)

    # Dummy results – in real life this would call Whisper + sentiment model
    combined_text = " ".join(packets)
    transcription = f"[Transcribed] {combined_text[:150]}..." if combined_text else "No audio data received"
    
    sentiment = random.choice(["positive", "negative", "neutral", "mixed"])
    
    logger.info(f"Mock AI completed: sentiment={sentiment}")
    return transcription, sentiment
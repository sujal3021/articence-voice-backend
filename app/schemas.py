# app/schemas.py
from pydantic import BaseModel, Field


class AudioPacket(BaseModel):
    """
    Represents one chunk/packet of simulated audio metadata received for a call.
    This is what clients POST to /v1/call/stream/{call_id}
    """
    sequence: int = Field(..., ge=1, description="Sequence number of this packet (must be positive integer)")
    data: str = Field(..., description="Base64-encoded or raw string representing the audio chunk/metadata")
    timestamp: float = Field(..., description="Unix timestamp when this packet was captured/sent")
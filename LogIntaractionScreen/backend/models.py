#
# Pydantic models for data validation and serialization.
#
from pydantic import BaseModel
from typing import List, Optional

class InteractionBase(BaseModel):
    """Base model for an HCP interaction, defining common fields."""
    hcpName: Optional[str] = None
    interactionType: Optional[str] = None
    interactionDate: Optional[str] = None
    summary: Optional[str] = None
    discussionTopics: Optional[List[str]] = None
    sentiment: Optional[str] = None
    outcomes: Optional[str] = None
    followUp: Optional[str] = None

class ChatMessage(BaseModel):
    """Model for a single chat message."""
    sender: str  # 'user' or 'agent'
    text: str

class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    message: str
    chatHistory: List[ChatMessage]
    interactionId: Optional[int] = None # To hold the active interaction context ID

class PopulateRequest(BaseModel):
    message: str

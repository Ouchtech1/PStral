"""
Conversations API endpoints for Pstral.
Manages user chat history.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel

from ....core.auth import User, get_current_active_user
from ....infrastructure.database.conversations_db import (
    Conversation,
    ConversationSummary,
    Message,
    create_conversation,
    get_conversation,
    get_user_conversations,
    update_conversation,
    delete_conversation,
    search_conversations
)

router = APIRouter()


class CreateConversationRequest(BaseModel):
    id: str
    mode: str
    title: Optional[str] = "Nouvelle discussion"


class UpdateConversationRequest(BaseModel):
    messages: List[dict]
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    mode: str
    messages: List[dict]
    created_at: str
    updated_at: str


class ConversationsListResponse(BaseModel):
    conversations: List[ConversationSummary]
    total: int


@router.get("/", response_model=ConversationsListResponse)
async def list_conversations(
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user)
):
    """Get all conversations for the current user."""
    conversations = get_user_conversations(current_user.id, limit)
    return ConversationsListResponse(
        conversations=conversations,
        total=len(conversations)
    )


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new conversation."""
    conversation = create_conversation(
        user_id=current_user.id,
        conversation_id=request.id,
        mode=request.mode,
        title=request.title or "Nouvelle discussion"
    )
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        mode=conversation.mode,
        messages=[],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_single_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific conversation."""
    conversation = get_conversation(conversation_id, current_user.id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation non trouvée"
        )
    
    return ConversationResponse(
        id=conversation.id,
        title=conversation.title,
        mode=conversation.mode,
        messages=[m.dict() for m in conversation.messages],
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    )


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_existing_conversation(
    conversation_id: str,
    request: UpdateConversationRequest,
    current_user: User = Depends(get_current_active_user)
):
    """Update a conversation's messages or title."""
    # Check if conversation exists
    conversation = get_conversation(conversation_id, current_user.id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation non trouvée"
        )
    
    success = update_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id,
        messages=request.messages,
        title=request.title
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Échec de la mise à jour"
        )
    
    # Fetch updated conversation
    updated = get_conversation(conversation_id, current_user.id)
    
    return ConversationResponse(
        id=updated.id,
        title=updated.title,
        mode=updated.mode,
        messages=[m.dict() for m in updated.messages],
        created_at=updated.created_at,
        updated_at=updated.updated_at
    )


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_existing_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Delete a conversation."""
    success = delete_conversation(conversation_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation non trouvée"
        )
    
    return None


@router.get("/search/query", response_model=ConversationsListResponse)
async def search_user_conversations(
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_active_user)
):
    """Search conversations by title or content."""
    conversations = search_conversations(current_user.id, q, limit)
    return ConversationsListResponse(
        conversations=conversations,
        total=len(conversations)
    )


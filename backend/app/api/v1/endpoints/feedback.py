from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.infrastructure.database.feedback_db import add_feedback

router = APIRouter()

class FeedbackModel(BaseModel):
    user_question: str
    agent_answer: str
    rating: str  # "like" or "dislike"
    reason: Optional[str] = None

@router.post("/", status_code=201)
def submit_feedback(feedback: FeedbackModel):
    try:
        add_feedback(
            user_question=feedback.user_question,
            agent_answer=feedback.agent_answer,
            rating=feedback.rating,
            reason=feedback.reason
        )
        return {"message": "Feedback received"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

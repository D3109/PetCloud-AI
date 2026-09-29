from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.ai import AssistantRequest, AssistantResponse, RecommendationResponse
from app.services import ai_service

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@router.post("/assistant", response_model=AssistantResponse)
def assistant(data: AssistantRequest, current_user: User = Depends(get_current_user)):
    reply = ai_service.get_assistant_reply(data.message)
    return AssistantResponse(reply=reply)


@router.get("/recommendations/{customer_id}", response_model=RecommendationResponse)
def recommendations(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recent_categories = ["Alimento"]
    text = ai_service.get_recommendations(current_user.full_name or "cliente", recent_categories)
    return RecommendationResponse(customer_id=customer_id, recommendations=text)

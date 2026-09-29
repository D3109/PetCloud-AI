from pydantic import BaseModel


class AssistantRequest(BaseModel):
    message: str


class AssistantResponse(BaseModel):
    reply: str


class RecommendationResponse(BaseModel):
    customer_id: int
    recommendations: str

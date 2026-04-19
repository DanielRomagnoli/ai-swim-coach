from fastapi import APIRouter
from pydantic import BaseModel
from app.services.llm import ask_coach

router = APIRouter()

class ChatRequest(BaseModel):
    question: str
    context: dict = None


@router.post("/chat")
async def chat(req: ChatRequest):
    response = ask_coach(req.question, req.context)
    return {"response": response}
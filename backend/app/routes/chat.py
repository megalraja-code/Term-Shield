from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.database import get_db
from app.models import User, Analysis
from app.auth import get_current_user
from app.services.chatbot import answer_question
from app.services.embedder import _faiss_store, build_index

router = APIRouter()

class ChatRequest(BaseModel):
    analysis_id: int
    question: str

@router.post("/")
async def chat(req: ChatRequest, db: AsyncSession = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    if not req.question.strip(): raise HTTPException(400, "Question cannot be empty")
    row = (await db.execute(select(Analysis).where(
        Analysis.id == req.analysis_id, Analysis.user_id == current_user.id)
    )).scalar_one_or_none()
    if not row: raise HTTPException(404, "Analysis not found")
    if req.analysis_id not in _faiss_store: build_index(req.analysis_id, row.content)
    return answer_question(req.analysis_id, req.question)

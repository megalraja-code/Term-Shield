from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional

from app.database import get_db
from app.models import User, Analysis
from app.auth import get_current_user

from app.services.parser import (
    parse_pdf,
    parse_docx,
    parse_url,
    clean_text
)

from app.services.risk_detector import detect_risks
from app.services.summarizer import generate_summaries
from app.services.embedder import build_index, _faiss_store

import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/analyze")
async def analyze(
    source_type: str = Form(...),
    file: Optional[UploadFile] = File(None),
    text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    content = ""
    source_name = ""

    try:

        if source_type == "pdf" and file:
            content = parse_pdf(await file.read())
            source_name = file.filename

        elif source_type == "docx" and file:
            content = parse_docx(await file.read())
            source_name = file.filename

        elif source_type == "url" and url:
            content = parse_url(url)
            source_name = url[:120]

        elif source_type == "text" and text:
            content = clean_text(text)
            source_name = "Pasted Text"

        else:
            raise HTTPException(
                status_code=400,
                detail="Provide valid file, URL, or text"
            )

    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e)
        )

    if len(content) < 80:
        raise HTTPException(
            status_code=400,
            detail="Document too short or invalid"
        )

    s = generate_summaries(content)

    r = detect_risks(content)

    rec = Analysis(
        user_id=1,
        source_type=source_type,
        source_name=source_name,
        content=content[:50000],

        summary=s["short_summary"],

        eli15=s["easy_explanation"],

        risk_score=r["risk_score"],

        risk_level=r["risk_level"],

        risks=r["risks"]
    )

    db.add(rec)

    await db.flush()

    await db.refresh(rec)

    build_index(rec.id, content)

    return {
        "id": rec.id,

        "source_name": source_name,

        "source_type": source_type,

        "safe_or_risky": s["safe_or_risky"],

        "summary": s["short_summary"],

        "main_points": s["main_points"],

        "simple_explanation": s["easy_explanation"],

        "eli15": s["easy_explanation"],

        "risk_score": r["risk_score"],

        "risk_level": r["risk_level"],

        "risks": r["risks"],

        "created_at": rec.created_at.isoformat()
    }


@router.get("/history")
async def history(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    rows = await db.execute(
        select(Analysis)
        .where(Analysis.user_id == current_user.id)
        .order_by(desc(Analysis.created_at))
        .limit(30)
    )

    return [
        {
            "id": a.id,
            "source_name": a.source_name,
            "source_type": a.source_type,
            "risk_score": a.risk_score,
            "risk_level": a.risk_level,
            "created_at": a.created_at.isoformat()
        }
        for a in rows.scalars().all()
    ]


@router.get("/{aid}")
async def get_analysis(
    aid: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    row = (
        await db.execute(
            select(Analysis).where(
                Analysis.id == aid,
                Analysis.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()

    if not row:
        raise HTTPException(404, "Analysis not found")

    if aid not in _faiss_store:
        build_index(aid, row.content)

    return {
        "id": row.id,

        "source_name": row.source_name,

        "source_type": row.source_type,

        "summary": row.summary,

        "simple_explanation": row.summary,

        "eli15": row.eli15,

        "risk_score": row.risk_score,

        "risk_level": row.risk_level,

        "risks": row.risks,

        "created_at": row.created_at.isoformat()
    }


@router.delete("/{aid}")
async def delete_analysis(
    aid: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    row = (
        await db.execute(
            select(Analysis).where(
                Analysis.id == aid,
                Analysis.user_id == current_user.id
            )
        )
    ).scalar_one_or_none()

    if not row:
        raise HTTPException(404, "Analysis not found")

    await db.delete(row)

    _faiss_store.pop(aid, None)

    return {
        "message": "Deleted"
    }
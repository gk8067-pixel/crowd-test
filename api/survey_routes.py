from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import MetaData, Table, Column, Integer, String, Text, select, insert
from .database import engine

metadata = MetaData()

surveys = Table(
    "surveys",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(200), nullable=False),
    Column("description", Text),
)

# 啟動時若表不存在就建立（方便你先測）
metadata.create_all(engine, checkfirst=True)

router = APIRouter(prefix="/surveys", tags=["surveys"])

class SurveyIn(BaseModel):
    title: str
    description: str | None = None

class SurveyOut(SurveyIn):
    id: int

@router.post("", response_model=SurveyOut)
def create_survey(payload: SurveyIn):
    with engine.begin() as conn:
        result = conn.execute(
            insert(surveys)
            .values(title=payload.title, description=payload.description)
            .returning(surveys.c.id)
        )
        new_id = result.scalar_one()
        row = conn.execute(select(surveys).where(surveys.c.id == new_id)).mappings().one()
        return SurveyOut(**row)

@router.get("", response_model=list[SurveyOut])
def list_surveys():
    with engine.begin() as conn:
        rows = conn.execute(select(surveys).order_by(surveys.c.id.desc())).mappings().all()
        return [SurveyOut(**r) for r in rows]

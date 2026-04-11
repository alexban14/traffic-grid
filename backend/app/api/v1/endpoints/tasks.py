from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from app.db.session import get_db
from app.models.task import Task
from app.schemas.task import TaskResponse

router = APIRouter()


@router.get("/", response_model=List[TaskResponse])
async def list_tasks(limit: int = 50, db: Session = Depends(get_db)):
    tasks = db.exec(
        select(Task).order_by(Task.created_at.desc()).limit(limit)
    ).all()
    return tasks


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

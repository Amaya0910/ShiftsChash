"""Rutas HTTP de metas de ahorro. La lógica vive en services.saving_service."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..services import saving_service

router = APIRouter(prefix="/saving-goals", tags=["saving-goals"])


@router.get("/", response_model=list[schemas.SavingGoalOut])
def list_saving_goals(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    goals = db.query(models.SavingGoal).filter(models.SavingGoal.user_id == current_user.user_id).all()
    return [saving_service.to_goal_out(g) for g in goals]


@router.get("/{goal_id}", response_model=schemas.SavingGoalOut)
def get_saving_goal_detail(
    goal_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    goal = saving_service.get_owned_goal(db, current_user.user_id, goal_id)
    return saving_service.to_goal_out(goal)


@router.post("/", response_model=schemas.SavingGoalOut)
def create_saving_goal(
    goal: schemas.SavingGoalCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    return saving_service.to_goal_out(saving_service.create_goal(db, current_user, goal))


@router.put("/{goal_id}", response_model=schemas.SavingGoalOut)
def update_saving_goal(
    goal_id: int,
    goal_update: schemas.SavingGoalUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    goal = saving_service.get_owned_goal(db, current_user.user_id, goal_id)
    goal = saving_service.update_goal(db, current_user, goal, goal_update)
    return saving_service.to_goal_out(goal)


@router.delete("/{goal_id}")
def delete_saving_goal(
    goal_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    goal = saving_service.get_owned_goal(db, current_user.user_id, goal_id)
    db.delete(goal)
    db.commit()
    return {"message": "Meta de ahorro eliminada exitosamente"}


@router.post("/{goal_id}/toggle-day/{day_number}")
def toggle_day(
    goal_id: int,
    day_number: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    goal = saving_service.get_owned_goal(db, current_user.user_id, goal_id)
    return saving_service.toggle_day(db, goal, day_number)

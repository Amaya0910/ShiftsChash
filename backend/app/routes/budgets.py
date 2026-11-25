"""Rutas HTTP de presupuestos. La lógica vive en services.budget_service."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db
from ..services import budget_service

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("/", response_model=list[schemas.BudgetOut])
def get_budgets(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene todos los presupuestos del usuario actual."""
    budgets = db.query(models.Budget).filter(models.Budget.user_id == current_user.user_id).all()
    return [budget_service.to_budget_out(db, b) for b in budgets]


@router.post("/", response_model=schemas.BudgetOut, status_code=status.HTTP_201_CREATED)
def create_budget(
    data: schemas.BudgetCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Crea un nuevo presupuesto para el usuario actual."""
    budget = budget_service.create_budget(db, current_user.user_id, data)
    return budget_service.to_budget_out(db, budget)


@router.put("/{budget_id}", response_model=schemas.BudgetOut)
def update_budget(
    budget_id: int,
    data: schemas.BudgetUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza un presupuesto existente (solo el propietario puede hacerlo)."""
    budget = budget_service.get_owned_budget(db, current_user.user_id, budget_id)
    budget = budget_service.update_budget(db, budget, data)
    return budget_service.to_budget_out(db, budget)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina un presupuesto (solo el propietario puede hacerlo)."""
    budget = budget_service.get_owned_budget(db, current_user.user_id, budget_id)
    db.delete(budget)
    db.commit()

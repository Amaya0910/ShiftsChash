"""Reglas de negocio de los presupuestos: período, gasto y porcentaje consumido."""
import calendar
from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from .category_service import get_accessible_category


def _reference_date(budget, today: date) -> date:
    """Fecha que fija el período: hoy si es permanente; si no, start_date (o hoy)."""
    if budget.is_permanent or not budget.start_date:
        return today
    return budget.start_date


def _daily_range(budget, today: date) -> tuple:
    day = _reference_date(budget, today)
    return day, day


def _weekly_range(budget, today: date) -> tuple:
    day = _reference_date(budget, today)
    monday = day - timedelta(days=day.weekday())
    return monday, monday + timedelta(days=6)


def _monthly_range(budget, today: date) -> tuple:
    use_today = budget.is_permanent
    month = today.month if use_today or not budget.month else budget.month
    year = today.year if use_today or not budget.year else budget.year
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


def _unique_range(budget, _today: date) -> tuple:
    return budget.start_date, budget.end_date


_RANGES = {
    "daily": _daily_range,
    "weekly": _weekly_range,
    "monthly": _monthly_range,
    "unique": _unique_range,
}


def get_date_range(budget, today: date = None) -> tuple:
    """Rango (inicio, fin) inclusivo del período del presupuesto."""
    today = today or date.today()
    calcular = _RANGES.get(budget.period_type)
    return calcular(budget, today) if calcular else (today, today)


def calculate_spent(db: Session, budget: models.Budget) -> float:
    """Suma los gastos del dueño del presupuesto en su categoría y período."""
    start, end = get_date_range(budget)
    rows = db.query(models.Transaction.amount).filter(
        models.Transaction.user_id == budget.user_id,
        models.Transaction.category_id == budget.category_id,
        models.Transaction.type == "expense",
        models.Transaction.trans_date >= start,
        models.Transaction.trans_date <= end,
    ).all()
    return sum(float(amount) for (amount,) in rows)


def percentage_used(spent: float, amount: float) -> float:
    """Porcentaje real consumido; puede superar 100 (D-04)."""
    return round(spent / amount * 100, 2) if amount > 0 else 0


def to_budget_out(db: Session, budget: models.Budget) -> schemas.BudgetOut:
    """Construye la respuesta del presupuesto con su gasto y porcentaje."""
    spent = calculate_spent(db, budget)
    return schemas.BudgetOut(
        budget_id=budget.budget_id,
        category_id=budget.category_id,
        name=budget.name,
        amount=float(budget.amount),
        period_type=budget.period_type,
        month=budget.month,
        year=budget.year,
        start_date=budget.start_date,
        end_date=budget.end_date,
        is_permanent=budget.is_permanent,
        category_name=budget.category.name_cat,
        category_icon=budget.category.icon,
        spent=spent,
        percentage=percentage_used(spent, float(budget.amount)),
    )


def get_owned_budget(db: Session, user_id: int, budget_id: int) -> models.Budget:
    """Devuelve el presupuesto del usuario o responde 404."""
    budget = db.query(models.Budget).filter(
        models.Budget.budget_id == budget_id,
        models.Budget.user_id == user_id,
    ).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Presupuesto no encontrado o no pertenece al usuario",
        )
    return budget


def create_budget(db: Session, user_id: int, data: schemas.BudgetCreate) -> models.Budget:
    get_accessible_category(db, user_id, data.category_id)
    budget = models.Budget(user_id=user_id, **data.model_dump())
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def update_budget(db: Session, budget: models.Budget, data: schemas.BudgetUpdate) -> models.Budget:
    """Aplica solo los campos enviados (los nulos se ignoran)."""
    changes = data.model_dump(exclude_none=True)
    if "category_id" in changes:
        get_accessible_category(db, budget.user_id, changes["category_id"])
    for field, value in changes.items():
        setattr(budget, field, value)
    db.commit()
    db.refresh(budget)
    return budget

"""Reglas de negocio de las metas de ahorro: plan de cuotas diarias y progreso."""
import json
import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_FLOOR, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from .. import models, schemas

# Unidad mínima de redondeo por moneda
CURRENCY_CONFIG = {
    "COP": {"min_unit": 100, "decimal_places": 0},
    "USD": {"min_unit": 0.01, "decimal_places": 2},
    "EUR": {"min_unit": 0.01, "decimal_places": 2},
    "MXN": {"min_unit": 0.01, "decimal_places": 2},
}
DEFAULT_CURRENCY = "COP"
DEFAULT_DURATION_DAYS = 30


def get_min_unit(currency: str = DEFAULT_CURRENCY) -> float:
    return CURRENCY_CONFIG.get(currency.upper(), CURRENCY_CONFIG[DEFAULT_CURRENCY])["min_unit"]


def round_to_unit(value: float, unit: float) -> float:
    """Redondea value al múltiplo más cercano de unit (con Decimal, sin errores de coma flotante)."""
    if unit <= 0:
        return value
    d_unit = Decimal(str(unit))
    rounded = (Decimal(str(value)) / d_unit).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * d_unit
    return float(rounded)


def _distribute_insufficient(target: float, num_days: int, min_unit: float) -> dict:
    """D-01: el objetivo no alcanza para dar min_unit a cada día.

    Los primeros floor(target / min_unit) días reciben min_unit, el resto 0 y el
    último día absorbe el residuo (siempre >= 0): ninguna cuota queda negativa.
    """
    d_unit = Decimal(str(min_unit))
    units = int((Decimal(str(target)) / d_unit).to_integral_value(rounding=ROUND_FLOOR))
    amounts = {str(i): float(d_unit) if i <= units else 0.0 for i in range(1, num_days)}
    amounts[str(num_days)] = round_to_unit(target - sum(amounts.values()), min_unit)
    return amounts


def _distribute_variable(target: float, num_days: int, min_unit: float) -> dict:
    """Reparte target con una variación de ±30 % por día (semilla determinista)."""
    rng = random.Random(int(target))
    amounts = {}
    remaining = target
    for i in range(1, num_days):
        days_left = num_days - i
        max_today = round_to_unit(remaining - days_left * min_unit, min_unit)
        amount = round_to_unit(remaining / (days_left + 1) * rng.uniform(0.7, 1.3), min_unit)
        amount = max(min_unit, min(amount, max_today))
        amounts[str(i)] = amount
        remaining = round_to_unit(remaining - amount, min_unit)
    amounts[str(num_days)] = round_to_unit(remaining, min_unit)
    return amounts


def generate_daily_amounts(start_date: date, end_date: date, target_amount: Decimal,
                           currency: str = DEFAULT_CURRENCY) -> dict:
    """Plan de cuotas diarias redondeadas a la unidad mínima de la moneda.

    La suma es exactamente target_amount y ninguna cuota es negativa.
    """
    end_date = end_date or start_date + timedelta(days=DEFAULT_DURATION_DAYS)
    num_days = (end_date - start_date).days + 1
    if num_days <= 0:
        raise ValueError("La fecha de fin debe ser después de la fecha de inicio")

    target = float(target_amount)
    min_unit = get_min_unit(currency)
    if num_days == 1:
        return {"1": round_to_unit(target, min_unit)}
    if target < num_days * min_unit:
        return _distribute_insufficient(target, num_days, min_unit)
    return _distribute_variable(target, num_days, min_unit)


def calculate_progress(completed_days: list, daily_amounts: dict, target_amount: float) -> dict:
    total_saved = sum(daily_amounts.get(str(day), 0) for day in completed_days)
    percentage = (total_saved / target_amount * 100) if target_amount > 0 else 0
    return {
        "total_saved": round(total_saved, 2),
        "percentage": round(percentage, 2),
        "days_completed": len(completed_days),
        "total_days": len(daily_amounts),
    }


def _as_list(value) -> list:
    return value if isinstance(value, list) else json.loads(value or "[]")


def _as_dict(value) -> dict:
    return value if isinstance(value, dict) else json.loads(value or "{}")


def goal_progress(goal: models.SavingGoal) -> dict:
    return calculate_progress(_as_list(goal.completed_days), _as_dict(goal.daily_amounts),
                              float(goal.target_amount))


def to_goal_out(goal: models.SavingGoal) -> schemas.SavingGoalOut:
    """Construye la respuesta de la meta con su progreso calculado."""
    return schemas.SavingGoalOut(
        goal_id=goal.goal_id,
        user_id=goal.user_id,
        name=goal.name,
        target_amount=float(goal.target_amount),
        start_date=goal.start_date,
        end_date=goal.end_date,
        image_url=goal.image_url,
        completed_days=_as_list(goal.completed_days),
        daily_amounts=_as_dict(goal.daily_amounts),
        progress=goal_progress(goal),
        created_at=goal.created_at,
    )


def get_owned_goal(db: Session, user_id: int, goal_id: int) -> models.SavingGoal:
    """Devuelve la meta del usuario o responde 404."""
    goal = db.query(models.SavingGoal).filter(
        models.SavingGoal.goal_id == goal_id,
        models.SavingGoal.user_id == user_id,
    ).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")
    return goal


def create_goal(db: Session, user: models.User, data: schemas.SavingGoalCreate) -> models.SavingGoal:
    start = data.start_date or date.today()
    # D-07: sin fecha final se usa la misma duración por defecto del plan y se guarda
    end = data.end_date or start + timedelta(days=DEFAULT_DURATION_DAYS)
    if end < start:
        raise HTTPException(status_code=422, detail="La fecha de inicio no puede ser posterior a la fecha final")

    goal = models.SavingGoal(
        user_id=user.user_id,
        name=data.name,
        target_amount=data.target_amount,
        start_date=start,
        end_date=end,
        image_url=data.image_url,
        completed_days=[],
        # D-08: el plan usa la moneda configurada por el usuario
        daily_amounts=generate_daily_amounts(start, end, Decimal(str(data.target_amount)),
                                             user.currency or DEFAULT_CURRENCY),
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


def update_goal(db: Session, user: models.User, goal: models.SavingGoal,
                data: schemas.SavingGoalUpdate) -> models.SavingGoal:
    """Aplica los campos enviados; si cambian el objetivo o la fecha final, rehace el plan."""
    changes = data.model_dump(exclude_unset=True)
    plan_changed = any(
        field in changes and getattr(goal, field) != changes[field]
        for field in ("target_amount", "end_date")
    )
    for field, value in changes.items():
        setattr(goal, field, value)

    if plan_changed:
        goal.daily_amounts = generate_daily_amounts(goal.start_date, goal.end_date,
                                                    Decimal(str(goal.target_amount)),
                                                    user.currency or DEFAULT_CURRENCY)
        flag_modified(goal, "daily_amounts")
        # D-15: los días marcados que ya no existen en el plan nuevo dejan de contar
        goal.completed_days = [d for d in _as_list(goal.completed_days) if str(d) in goal.daily_amounts]
        flag_modified(goal, "completed_days")

    db.commit()
    db.refresh(goal)
    return goal


def toggle_day(db: Session, goal: models.SavingGoal, day_number: int) -> dict:
    """Marca o desmarca un día del plan y devuelve el progreso actualizado."""
    # D-15: solo existen los días del plan (1..N); otro número inflaba el progreso
    if str(day_number) not in _as_dict(goal.daily_amounts):
        raise HTTPException(status_code=422, detail="Ese día no pertenece al plan de la meta")
    completed = list(_as_list(goal.completed_days))
    if day_number in completed:
        completed.remove(day_number)
        action = "desmarcado"
    else:
        completed.append(day_number)
        action = "marcado"

    goal.completed_days = completed
    flag_modified(goal, "completed_days")
    db.commit()
    db.refresh(goal)
    return {
        "goal_id": goal.goal_id,
        "day_number": day_number,
        "action": action,
        "completed_days": completed,
        "progress": goal_progress(goal),
    }

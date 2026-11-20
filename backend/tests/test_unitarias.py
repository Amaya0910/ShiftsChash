"""Pruebas unitarias (caja negra y caja blanca) de la lógica de negocio.

Corresponden a la Segunda Parte, sección 3 del documento: clases de
equivalencia, valores límite y caminos básicos de generate_daily_amounts,
get_date_range y _toca_hoy.
"""
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app import schemas
from app.routes.budgets import get_date_range
from app.routes.savings import calculate_progress, generate_daily_amounts
from app.scheduler import _toca_hoy


# ── F3: generate_daily_amounts ────────────────────────────────────────────────
CASOS_PLAN = [
    # (días, objetivo, moneda)
    (1, 50_000, "COP"),          # camino: un solo día
    (15, 1_000, "COP"),          # camino: objetivo insuficiente (D-01)
    (30, 2_000, "COP"),          # objetivo insuficiente, varios residuos
    (10, 999, "COP"),            # objetivo no múltiplo de la unidad
    (30, 300_000, "COP"),        # camino normal
    (365, 10_000_000, "COP"),    # plan largo
    (30, 1_500.50, "USD"),       # moneda con centavos
    (2, 1_000, "COP"),           # valor límite: dos días
]


@pytest.mark.parametrize("dias,objetivo,moneda", CASOS_PLAN)
def test_plan_suma_objetivo_y_sin_negativos(dias, objetivo, moneda):
    inicio = date(2026, 11, 1)
    plan = generate_daily_amounts(inicio, inicio + timedelta(days=dias - 1), Decimal(str(objetivo)), moneda)
    assert len(plan) == dias
    assert all(v >= 0 for v in plan.values()), "ninguna cuota puede ser negativa (D-01)"
    unidad = 100 if moneda == "COP" else 0.01
    objetivo_redondeado = round(objetivo / unidad) * unidad
    assert sum(plan.values()) == pytest.approx(objetivo_redondeado, abs=unidad)


def test_d01_caso_reportado_1000_en_15_dias():
    inicio = date(2026, 11, 1)
    plan = generate_daily_amounts(inicio, inicio + timedelta(days=14), Decimal("1000"), "COP")
    assert plan["15"] >= 0
    assert sum(plan.values()) == 1000
    assert all(v % 100 == 0 for v in plan.values())


def test_plan_es_determinista():
    inicio = date(2026, 1, 1)
    a = generate_daily_amounts(inicio, date(2026, 1, 31), Decimal("310000"))
    b = generate_daily_amounts(inicio, date(2026, 1, 31), Decimal("310000"))
    assert a == b


def test_plan_fecha_fin_anterior_lanza_error():
    with pytest.raises(ValueError):
        generate_daily_amounts(date(2026, 1, 10), date(2026, 1, 1), Decimal("1000"))


def test_plan_sin_fecha_fin_usa_31_dias():
    plan = generate_daily_amounts(date(2026, 1, 1), None, Decimal("310000"))
    assert len(plan) == 31


def test_calculate_progress():
    p = calculate_progress([1, 2], {"1": 100.0, "2": 300.0, "3": 600.0}, 1000)
    assert p == {"total_saved": 400.0, "percentage": 40.0, "days_completed": 2, "total_days": 3}
    assert calculate_progress([], {}, 0)["percentage"] == 0


# ── F2: get_date_range ────────────────────────────────────────────────────────
def _b(**kw):
    base = dict(period_type="monthly", is_permanent=False, start_date=None, end_date=None, month=None, year=None)
    base.update(kw)
    return SimpleNamespace(**base)


def test_rango_diario_con_fecha():
    d = date(2026, 3, 4)
    assert get_date_range(_b(period_type="daily", start_date=d)) == (d, d)


def test_rango_diario_permanente_usa_hoy():
    hoy = date.today()
    assert get_date_range(_b(period_type="daily", is_permanent=True, start_date=date(2020, 1, 1))) == (hoy, hoy)


def test_rango_semanal_lunes_a_domingo():
    ini, fin = get_date_range(_b(period_type="weekly", start_date=date(2026, 11, 19)))  # jueves
    assert ini == date(2026, 11, 16) and ini.weekday() == 0
    assert fin == date(2026, 11, 22) and fin.weekday() == 6


@pytest.mark.parametrize("mes,anio,ultimo", [(2, 2028, 29), (2, 2026, 28), (12, 2026, 31), (1, 2026, 31), (4, 2026, 30)])
def test_rango_mensual_valores_limite(mes, anio, ultimo):
    assert get_date_range(_b(month=mes, year=anio)) == (date(anio, mes, 1), date(anio, mes, ultimo))


def test_rango_mensual_permanente_ignora_mes():
    hoy = date.today()
    ini, _ = get_date_range(_b(month=1, year=2000, is_permanent=True))
    assert ini == date(hoy.year, hoy.month, 1)


def test_rango_unico():
    a, b = date(2026, 1, 5), date(2026, 2, 5)
    assert get_date_range(_b(period_type="unique", start_date=a, end_date=b)) == (a, b)


def test_rango_por_defecto():
    hoy = date.today()
    assert get_date_range(_b(period_type="otro")) == (hoy, hoy)


# ── F1: _toca_hoy (recurrencias) ──────────────────────────────────────────────
def _t(freq, d=date(2026, 1, 31)):
    return SimpleNamespace(frequency=freq, trans_date=d)


@pytest.mark.parametrize("freq,hoy,esperado", [
    ("monthly", date(2026, 3, 31), True),
    ("monthly", date(2026, 3, 30), False),
    ("weekly", date(2026, 2, 7), True),
    ("weekly", date(2026, 2, 8), False),
    ("biweekly", date(2026, 2, 14), True),
    ("biweekly", date(2026, 2, 7), False),
    ("annual", date(2027, 1, 31), True),
    ("annual", date(2027, 2, 28), False),
    ("monthly", date(2026, 1, 1), False),   # antes de la fecha original
    ("otra", date(2026, 3, 31), False),     # frecuencia desconocida
])
def test_toca_hoy(freq, hoy, esperado):
    assert _toca_hoy(_t(freq), hoy) is esperado


def test_toca_hoy_sin_fecha():
    assert _toca_hoy(SimpleNamespace(frequency="monthly", trans_date=None), date.today()) is False


# ── Validaciones de esquemas (D-02, D-03) ─────────────────────────────────────
@pytest.mark.parametrize("monto", [0, -1, 10**13])
def test_transaccion_monto_invalido(monto):
    with pytest.raises(ValidationError):
        schemas.TransactionCreate(category_id=1, type="expense", amount=monto)


@pytest.mark.parametrize("monto", [0.01, 1, 9_999_999_999_999.99])
def test_transaccion_monto_valido(monto):
    assert schemas.TransactionCreate(category_id=1, type="expense", amount=monto).amount == monto


def test_transaccion_tipo_invalido():
    with pytest.raises(ValidationError):
        schemas.TransactionCreate(category_id=1, type="otro", amount=10)


@pytest.mark.parametrize("mes", [0, 13, -1])
def test_presupuesto_mes_invalido(mes):
    with pytest.raises(ValidationError):
        schemas.BudgetCreate(category_id=1, name="x", amount=10, period_type="monthly", month=mes, year=2026)


@pytest.mark.parametrize("mes", [1, 12])
def test_presupuesto_mes_limite_valido(mes):
    assert schemas.BudgetCreate(category_id=1, name="x", amount=10, period_type="monthly", month=mes, year=2026).month == mes


def test_presupuesto_unico_exige_fechas_ordenadas():
    with pytest.raises(ValidationError):
        schemas.BudgetCreate(category_id=1, name="x", amount=10, period_type="unique")
    with pytest.raises(ValidationError):
        schemas.BudgetCreate(category_id=1, name="x", amount=10, period_type="unique",
                             start_date=date(2026, 2, 1), end_date=date(2026, 1, 1))


def test_meta_fecha_pasada_y_orden():
    with pytest.raises(ValidationError):
        schemas.SavingGoalCreate(name="Viaje", target_amount=1000, end_date=date.today() - timedelta(days=1))
    with pytest.raises(ValidationError):
        schemas.SavingGoalCreate(name="Viaje", target_amount=1000,
                                 start_date=date.today() + timedelta(days=10), end_date=date.today() + timedelta(days=1))
    with pytest.raises(ValidationError):
        schemas.SavingGoalCreate(name="   ", target_amount=1000)

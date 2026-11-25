from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional, List, Dict
from datetime import date, datetime

# D-02: límite de Numeric(15,2) en la base de datos
MAX_AMOUNT = 9_999_999_999_999.99
# Frecuencias que entiende scheduler._toca_hoy
FRECUENCIAS = ("monthly", "weekly", "biweekly", "annual")


def _validar_monto(v, mensaje="El monto debe ser mayor a 0"):
    if v is None:
        return v
    if v <= 0:
        raise ValueError(mensaje)
    if v > MAX_AMOUNT:
        raise ValueError("El monto supera el máximo permitido (9.999.999.999.999,99)")
    return v


def _validar_mes(v):
    # D-03: un mes fuera de 1..12 provocaba ValueError (500) en get_date_range
    if v is not None and not 1 <= v <= 12:
        raise ValueError("El mes debe estar entre 1 y 12")
    return v


def _validar_anio(v):
    if v is not None and not 2000 <= v <= 2100:
        raise ValueError("El año debe estar entre 2000 y 2100")
    return v

# Authentication
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    user_id: int
    username: str
    email: str
    currency: str
    profile_pic: str | None = None  

    class Config:
        from_attributes = True

class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class GoogleAuthRequest(BaseModel):
    access_token: str

# Configuración de usuario
class UserUpdate(BaseModel):
    username: str
    email: EmailStr

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

class CurrencyUpdate(BaseModel):
    currency: str

# Categorías 
class CategoryOut(BaseModel):
    category_id: int
    name_cat: str
    icon: Optional[str]
    type: str
    is_default: int

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name_cat: str
    icon: Optional[str] = "⭐"
    type: str

    @field_validator("type")
    @classmethod
    def type_must_be_valid(cls, v):
        if v not in ("expense", "income", "both"):
            raise ValueError("Tipo inválido")
        return v

    @field_validator("name_cat")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

class CategoryUpdate(BaseModel):
    name_cat: str
    icon: Optional[str] = "⭐"
    type: str

# Transacciones
class TransactionCreate(BaseModel):
    category_id: int
    type: str
    amount: float
    description: Optional[str] = None
    trans_date: Optional[date] = None
    is_recurring: bool = False
    frequency: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        return _validar_monto(v)

    @field_validator("type")
    @classmethod
    def type_must_be_valid(cls, v):
        if v not in ("expense", "income"):
            raise ValueError("El tipo debe ser 'expense' o 'income'")
        return v

    @model_validator(mode="after")
    def recurring_requires_valid_frequency(self):
        # D-14: una recurrente sin frecuencia válida se guardaba y nunca se repetía
        if self.is_recurring and self.frequency not in FRECUENCIAS:
            raise ValueError("La frecuencia debe ser monthly, weekly, biweekly o annual")
        return self

class TransactionOut(BaseModel):
    trans_id: int
    category_id: int
    category_name: Optional[str] = None
    type: str
    amount: float
    description: Optional[str]
    trans_date: date
    is_recurring: bool = False
    frequency: Optional[str] = None

    class Config:
        from_attributes = True

# Presupuestos
class BudgetBase(BaseModel):
    category_id: int
    name: str
    amount: float
    period_type: str  # 'daily', 'weekly', 'monthly', 'unique'
    month: Optional[int] = None
    year: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_permanent: bool = False

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        return _validar_monto(v)

    @field_validator("period_type")
    @classmethod
    def period_type_must_be_valid(cls, v):
        if v not in ("daily", "weekly", "monthly", "unique"):
            raise ValueError("El tipo de período debe ser 'daily', 'weekly', 'monthly' o 'unique'")
        return v

    @field_validator("month")
    @classmethod
    def month_must_be_valid(cls, v):
        return _validar_mes(v)

    @field_validator("year")
    @classmethod
    def year_must_be_valid(cls, v):
        return _validar_anio(v)

class BudgetCreate(BudgetBase):
    @model_validator(mode="after")
    def unique_requires_dates(self):
        if self.period_type == "unique":
            if not self.start_date or not self.end_date:
                raise ValueError("El período único requiere fecha de inicio y fecha final")
            if self.start_date > self.end_date:
                raise ValueError("La fecha de inicio no puede ser posterior a la fecha final")
        return self

class BudgetUpdate(BaseModel):
    category_id: Optional[int] = None
    name: Optional[str] = None
    amount: Optional[float] = None
    period_type: Optional[str] = None
    month: Optional[int] = None
    year: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_permanent: Optional[bool] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        return _validar_monto(v)

    @field_validator("period_type")
    @classmethod
    def period_type_must_be_valid(cls, v):
        if v is not None and v not in ("daily", "weekly", "monthly", "unique"):
            raise ValueError("El tipo de período debe ser 'daily', 'weekly', 'monthly' o 'unique'")
        return v

    @field_validator("month")
    @classmethod
    def month_must_be_valid(cls, v):
        return _validar_mes(v)

    @field_validator("year")
    @classmethod
    def year_must_be_valid(cls, v):
        return _validar_anio(v)

class BudgetOut(BudgetBase):
    budget_id: int
    category_name: str
    category_icon: Optional[str]
    spent: float
    percentage: float

    class Config:
        from_attributes = True


# Metas de Ahorro
class SavingGoalCreate(BaseModel):
    name: str
    target_amount: float
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    image_url: Optional[str] = None

    @field_validator("target_amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        return _validar_monto(v, "El monto objetivo debe ser mayor a 0")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip()

    @field_validator("end_date")
    @classmethod
    def end_date_must_be_future(cls, v):
        if v and v < date.today():
            raise ValueError("La fecha de fin debe ser hoy o en el futuro")
        return v

    @model_validator(mode="after")
    def start_before_end(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha final")
        return self


class SavingGoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[float] = None
    end_date: Optional[date] = None
    image_url: Optional[str] = None

    @field_validator("target_amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        return _validar_monto(v, "El monto objetivo debe ser mayor a 0")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v.strip() if v else None


class SavingGoalOut(BaseModel):
    goal_id: int
    user_id: int
    name: str
    target_amount: float
    start_date: date
    end_date: date
    image_url: Optional[str]
    completed_days: List[int]
    daily_amounts: Dict[str, float]
    created_at: Optional[datetime] = None
    progress: Optional[Dict[str, float]] = None # Añadido para incluir el progreso calculado

    class Config:
        from_attributes = True

from sqlalchemy import Column, Integer, SmallInteger, String, Numeric, Date, TIMESTAMP, ForeignKey, text, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id     = Column(Integer, primary_key=True, index=True)
    username    = Column(String(25), nullable=False)
    email       = Column(String(150), nullable=False, unique=True)
    password    = Column(String(255), nullable=False)
    profile_pic = Column(String(150), nullable=True)
    currency    = Column(String(10), default="COP")
    created_at  = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # D-11: al eliminar la cuenta se eliminan sus datos (igual que ON DELETE CASCADE en la BD)
    categories    = relationship("Category", back_populates="user", foreign_keys="Category.user_id",
                                 cascade="all, delete-orphan")
    budgets       = relationship("Budget", back_populates="user", cascade="all, delete-orphan")
    transactions  = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    saving_goals  = relationship("SavingGoal", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "category"

    category_id = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=True)
    name_cat    = Column(String(25), nullable=False)
    icon        = Column(String(150), nullable=True)
    type        = Column(String(10), nullable=True)
    is_default  = Column(SmallInteger, default=0)

    user    = relationship("User", back_populates="categories", foreign_keys=[user_id])
    # D-11: los presupuestos de una categoría eliminada se eliminan con ella (ON DELETE CASCADE)
    budgets = relationship("Budget", back_populates="category", cascade="all, delete-orphan")


class Budget(Base):
    __tablename__ = "budget"

    budget_id    = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    category_id  = Column(Integer, ForeignKey("category.category_id", ondelete="CASCADE"), nullable=False)
    name         = Column(String(100), nullable=False)
    amount       = Column(Numeric(15, 2), nullable=False)
    period_type  = Column(String(10), nullable=False)  # 'daily', 'weekly', 'monthly', 'unique'
    month        = Column(SmallInteger, nullable=True)
    year         = Column(SmallInteger, nullable=True)
    start_date   = Column(Date, nullable=True)
    end_date     = Column(Date, nullable=True)
    is_permanent = Column(Boolean, default=False)  # True = presupuesto para siempre

    user     = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")


class Transaction(Base):
    __tablename__ = "transactions"

    trans_id     = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    category_id  = Column(Integer, ForeignKey("category.category_id", ondelete="RESTRICT"), nullable=False)
    type         = Column(String(15), nullable=False)
    amount       = Column(Numeric(15, 2), nullable=False)
    description  = Column(String(250), nullable=True)
    trans_date   = Column(Date, server_default=text("CURRENT_DATE"))
    is_recurring = Column(Boolean, default=False)        # ← nuevo
    frequency    = Column(String(15), nullable=True)     # ← nuevo

    user     = relationship("User", back_populates="transactions")
    category = relationship("Category")


class SavingGoal(Base):
    __tablename__ = "saving_goal"

    goal_id         = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    name            = Column(String(100), nullable=False)
    target_amount   = Column(Numeric(15, 2), nullable=False)
    start_date      = Column(Date, server_default=text("CURRENT_DATE"))
    end_date        = Column(Date, nullable=True)
    image_url       = Column(Text, nullable=True)
    completed_days  = Column(JSON, default=list)  # Lista de días completados: [1, 2, 5, ...]
    daily_amounts   = Column(JSON, default=dict)  # Mapeo de días a montos: {"1": 100.00, "2": 150.00, ...}
    created_at      = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    user = relationship("User", back_populates="saving_goals")
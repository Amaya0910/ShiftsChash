"""Acceso a las categorías visibles para un usuario (predeterminadas o propias)."""
from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .. import models


def visible_to(user_id: int):
    """Condición SQL: la categoría es predeterminada o pertenece al usuario."""
    return or_(models.Category.is_default == 1, models.Category.user_id == user_id)


def get_accessible_category(db: Session, user_id: int, category_id: int) -> models.Category:
    """Devuelve la categoría si el usuario puede usarla; si no, responde 404."""
    category = db.query(models.Category).filter(
        models.Category.category_id == category_id,
        visible_to(user_id),
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La categoría no existe o no pertenece al usuario",
        )
    return category

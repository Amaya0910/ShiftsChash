"""Configuración común de las pruebas del backend de ShiftCash.

Se usa una base de datos SQLite en memoria con claves foráneas activadas,
de modo que las pruebas no dependen de PostgreSQL ni de variables reales.
Con TEST_DATABASE_URL=postgresql://... corren sobre PostgreSQL.
"""
import os
import sys
import tempfile
from datetime import date

import pytest

# Las variables de entorno deben existir ANTES de importar la aplicación.
_DB_FILE = os.path.join(tempfile.mkdtemp(prefix="shiftcash_test_"), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_DB_FILE}"
os.environ.setdefault("SECRET_KEY", "clave-solo-para-pruebas")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import sessionmaker  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from app import models, scheduler  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

scheduler.scheduler.shutdown(wait=False)  # el cron real no debe correr en las pruebas

# Por defecto SQLite en memoria; con TEST_DATABASE_URL las pruebas corren sobre
# una base PostgreSQL vacía y desechable (por ejemplo, para PI-05).
_URL_PRUEBAS = os.environ.get("TEST_DATABASE_URL", "sqlite://")
if _URL_PRUEBAS.startswith("sqlite"):
    engine = create_engine(_URL_PRUEBAS, connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def _activar_fk(dbapi_connection, _):
        # PostgreSQL siempre aplica las FK; en SQLite hay que activarlas.
        dbapi_connection.execute("PRAGMA foreign_keys=ON")
else:
    engine = create_engine(_URL_PRUEBAS)


TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def base_limpia():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    db.add_all([
        models.Category(name_cat="Alimentación", icon="🍔", type="expense", is_default=1),
        models.Category(name_cat="Salario", icon="💼", type="income", is_default=1),
    ])
    db.commit()
    db.close()
    yield


@pytest.fixture
def db():
    s = TestingSession()
    yield s
    s.close()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)


def _registrar(client, email="ana@correo.com", username="ana"):
    r = client.post("/auth/register", json={"username": username, "email": email, "password": "Segura123"})
    assert r.status_code == 200, r.text
    r = client.post("/auth/login", json={"email": email, "password": "Segura123"})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture
def auth(client):
    return _registrar(client)


@pytest.fixture
def auth_otro(client):
    return _registrar(client, email="beto@correo.com", username="beto")


@pytest.fixture
def cat_gasto(db):
    return db.query(models.Category).filter_by(name_cat="Alimentación").first().category_id


@pytest.fixture
def hoy():
    return date.today()

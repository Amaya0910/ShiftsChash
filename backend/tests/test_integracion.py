"""Pruebas de integración API + ORM + base de datos (Segunda Parte, sección 4).

Cada prueba recorre un hilo completo: petición HTTP con JWT → FastAPI →
validación Pydantic → SQLAlchemy → base de datos, y verifica la respuesta.
"""
from datetime import date, timedelta

from app import models, scheduler


# ── Seguridad (D-06) ──────────────────────────────────────────────────────────
def test_d06_credenciales_codificadas_ya_no_funcionan(client):
    r = client.post("/auth/login", json={"email": "admin@test.com", "password": "123"})
    assert r.status_code == 401


def test_d06_token_de_usuario_999_rechazado(client):
    from app.auth import create_access_token
    token = create_access_token({"sub": "999"})
    r = client.get("/budgets/", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401


def test_sin_token_responde_401(client):
    assert client.get("/transactions/").status_code == 401
    assert client.get("/budgets/").status_code == 401
    assert client.get("/saving-goals/").status_code == 401


def test_registro_correo_duplicado(client, auth):
    r = client.post("/auth/register", json={"username": "otra", "email": "ana@correo.com", "password": "Segura123"})
    assert r.status_code == 400


def test_login_contrasena_incorrecta(client, auth):
    r = client.post("/auth/login", json={"email": "ana@correo.com", "password": "malamala"})
    assert r.status_code == 401


# ── F1: transacciones ─────────────────────────────────────────────────────────
def test_pi01_registrar_y_listar_transaccion(client, auth, cat_gasto):
    r = client.post("/transactions/", headers=auth, json={
        "category_id": cat_gasto, "type": "expense", "amount": 45000, "description": "Almuerzo"})
    assert r.status_code == 200, r.text
    assert r.json()["trans_date"] == date.today().isoformat()
    lista = client.get("/transactions/", headers=auth).json()
    assert [t["description"] for t in lista] == ["Almuerzo"]


def test_pi02_categoria_inexistente_404(client, auth):
    r = client.post("/transactions/", headers=auth, json={"category_id": 9999, "type": "expense", "amount": 10})
    assert r.status_code == 404


def test_pi03_monto_invalido_422(client, auth, cat_gasto):
    for monto in (0, -5, 10**14):
        r = client.post("/transactions/", headers=auth, json={"category_id": cat_gasto, "type": "expense", "amount": monto})
        assert r.status_code == 422


def test_aislamiento_entre_usuarios(client, auth, auth_otro, cat_gasto):
    client.post("/transactions/", headers=auth, json={"category_id": cat_gasto, "type": "expense", "amount": 10})
    assert client.get("/transactions/", headers=auth_otro).json() == []


def test_pi08_recurrente_genera_instancia_sin_duplicar(client, auth, cat_gasto, monkeypatch):
    from tests.conftest import TestingSession
    hace_un_mes = date.today().replace(day=1) - timedelta(days=1)
    hace_un_mes = hace_un_mes.replace(day=min(date.today().day, hace_un_mes.day))
    r = client.post("/transactions/", headers=auth, json={
        "category_id": cat_gasto, "type": "expense", "amount": 800000, "description": "Arriendo",
        "trans_date": hace_un_mes.isoformat(), "is_recurring": True, "frequency": "monthly"})
    assert r.status_code == 200
    monkeypatch.setattr(scheduler, "SessionLocal", TestingSession)
    debe_tocar = scheduler._toca_hoy(models.Transaction(trans_date=hace_un_mes, frequency="monthly"), date.today())
    scheduler.registrar_recurrentes()
    scheduler.registrar_recurrentes()  # segunda corrida: no debe duplicar
    lista = client.get("/transactions/", headers=auth).json()
    assert len(lista) == (2 if debe_tocar else 1)


# ── F2: presupuestos ──────────────────────────────────────────────────────────
def _presupuesto(client, auth, cat, **kw):
    hoy = date.today()
    body = {"category_id": cat, "name": "Comida", "amount": 600000, "period_type": "monthly",
            "month": hoy.month, "year": hoy.year}
    body.update(kw)
    return client.post("/budgets/", headers=auth, json=body)


def test_pi04_d04_porcentaje_supera_100(client, auth, cat_gasto):
    client.post("/transactions/", headers=auth, json={"category_id": cat_gasto, "type": "expense", "amount": 700000})
    r = _presupuesto(client, auth, cat_gasto)
    assert r.status_code == 201, r.text
    assert r.json()["spent"] == 700000
    assert r.json()["percentage"] > 100          # antes se limitaba a 100 (D-04)
    assert client.get("/budgets/", headers=auth).json()[0]["percentage"] > 100


def test_presupuesto_solo_suma_gastos_del_rango(client, auth, cat_gasto):
    hoy = date.today()
    otro_mes = (hoy.replace(day=1) - timedelta(days=1))
    client.post("/transactions/", headers=auth, json={"category_id": cat_gasto, "type": "expense", "amount": 100})
    client.post("/transactions/", headers=auth, json={"category_id": cat_gasto, "type": "expense", "amount": 999,
                                                      "trans_date": otro_mes.isoformat()})
    client.post("/transactions/", headers=auth, json={"category_id": cat_gasto, "type": "income", "amount": 555})
    assert _presupuesto(client, auth, cat_gasto).json()["spent"] == 100


def test_pi09_d03_mes_invalido_422(client, auth, cat_gasto):
    assert _presupuesto(client, auth, cat_gasto, month=13).status_code == 422


def test_presupuesto_ajeno_404(client, auth, auth_otro, cat_gasto):
    bid = _presupuesto(client, auth, cat_gasto).json()["budget_id"]
    assert client.put(f"/budgets/{bid}", headers=auth_otro, json={"amount": 1}).status_code == 404
    assert client.delete(f"/budgets/{bid}", headers=auth_otro).status_code == 404
    assert client.delete(f"/budgets/{bid}", headers=auth).status_code == 204


# ── Categorías (D-05) ─────────────────────────────────────────────────────────
def test_pi05_d05_no_elimina_categoria_con_transacciones(client, auth):
    cid = client.post("/categories/", headers=auth, json={"name_cat": "Mascotas", "type": "expense"}).json()["category_id"]
    client.post("/transactions/", headers=auth, json={"category_id": cid, "type": "expense", "amount": 20000})
    assert client.delete(f"/categories/{cid}", headers=auth).status_code == 409
    assert client.get("/transactions/", headers=auth).json()[0]["category_id"] == cid


def test_elimina_categoria_sin_transacciones(client, auth):
    cid = client.post("/categories/", headers=auth, json={"name_cat": "Libros", "type": "expense"}).json()["category_id"]
    assert client.delete(f"/categories/{cid}", headers=auth).status_code == 204


def test_no_elimina_categoria_predeterminada(client, auth, cat_gasto):
    assert client.delete(f"/categories/{cat_gasto}", headers=auth).status_code == 404


# ── F3: metas de ahorro ───────────────────────────────────────────────────────
def test_pi06_d01_meta_pequena_sin_cuotas_negativas(client, auth):
    fin = (date.today() + timedelta(days=14)).isoformat()
    r = client.post("/saving-goals/", headers=auth, json={"name": "Reto", "target_amount": 1000, "end_date": fin})
    assert r.status_code == 200, r.text
    cuotas = r.json()["daily_amounts"]
    assert len(cuotas) == 15 and min(cuotas.values()) >= 0 and sum(cuotas.values()) == 1000


def test_pi10_d07_meta_sin_fecha_final(client, auth):
    r = client.post("/saving-goals/", headers=auth, json={"name": "Viaje", "target_amount": 310000})
    assert r.status_code == 200, r.text
    assert r.json()["end_date"] == (date.today() + timedelta(days=30)).isoformat()


def test_d08_meta_usa_moneda_del_usuario(client, auth):
    assert client.put("/users/me/currency", headers=auth, json={"currency": "USD"}).status_code == 200
    fin = (date.today() + timedelta(days=2)).isoformat()
    r = client.post("/saving-goals/", headers=auth, json={"name": "USD", "target_amount": 100.5, "end_date": fin})
    cuotas = r.json()["daily_amounts"].values()
    assert any(round(v) != v for v in cuotas) or sum(cuotas) == 100.5  # COP redondearía a 100


def test_pi07_marcar_dias_y_progreso(client, auth):
    fin = (date.today() + timedelta(days=29)).isoformat()
    meta = client.post("/saving-goals/", headers=auth, json={"name": "Moto", "target_amount": 300000, "end_date": fin}).json()
    gid = meta["goal_id"]
    for d in (1, 2, 3):
        r = client.post(f"/saving-goals/{gid}/toggle-day/{d}", headers=auth)
    assert r.json()["progress"]["days_completed"] == 3
    r = client.post(f"/saving-goals/{gid}/toggle-day/2", headers=auth)
    assert r.json()["action"] == "desmarcado" and r.json()["completed_days"] == [1, 3]
    esperado = meta["daily_amounts"]["1"] + meta["daily_amounts"]["3"]
    assert r.json()["progress"]["total_saved"] == esperado


def test_editar_meta_regenera_plan(client, auth):
    fin = (date.today() + timedelta(days=9)).isoformat()
    gid = client.post("/saving-goals/", headers=auth, json={"name": "A", "target_amount": 100000, "end_date": fin}).json()["goal_id"]
    r = client.put(f"/saving-goals/{gid}", headers=auth, json={"target_amount": 200000})
    assert sum(r.json()["daily_amounts"].values()) == 200000


def test_meta_ajena_404(client, auth, auth_otro):
    gid = client.post("/saving-goals/", headers=auth, json={"name": "A", "target_amount": 1000}).json()["goal_id"]
    assert client.post(f"/saving-goals/{gid}/toggle-day/1", headers=auth_otro).status_code == 404
    assert client.delete(f"/saving-goals/{gid}", headers=auth_otro).status_code == 404

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


def test_pi01_sin_token_responde_401(client):
    assert client.get("/transactions/").status_code == 401
    assert client.get("/budgets/").status_code == 401
    assert client.get("/saving-goals/").status_code == 401


def test_rnf01_contrasena_se_guarda_con_hash_bcrypt(client, auth, db):
    guardada = db.query(models.User).filter_by(email="ana@correo.com").first().password
    assert guardada != "Segura123"
    assert guardada.startswith("$2")  # prefijo de bcrypt


def test_rnf03_cors_solo_origenes_permitidos(client):
    permitido = client.get("/", headers={"Origin": "http://localhost:5173"})
    ajeno = client.get("/", headers={"Origin": "https://sitio-ajeno.example"})
    assert permitido.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "access-control-allow-origin" not in ajeno.headers


def test_ps07_api_envia_cabecera_nosniff(client):
    assert client.get("/").headers.get("x-content-type-options") == "nosniff"


def test_registro_correo_duplicado(client, auth):
    r = client.post("/auth/register", json={"username": "otra", "email": "ana@correo.com", "password": "Segura123"})
    assert r.status_code == 400


def test_login_contrasena_incorrecta(client, auth):
    r = client.post("/auth/login", json={"email": "ana@correo.com", "password": "malamala"})
    assert r.status_code == 401


# ── F1: transacciones ─────────────────────────────────────────────────────────
def test_pi02_registrar_y_listar_transaccion(client, auth, cat_gasto):
    r = client.post("/transactions/", headers=auth, json={
        "category_id": cat_gasto, "type": "expense", "amount": 45000, "description": "Almuerzo"})
    assert r.status_code == 200, r.text
    assert r.json()["trans_date"] == date.today().isoformat()
    lista = client.get("/transactions/", headers=auth).json()
    assert [t["description"] for t in lista] == ["Almuerzo"]


def test_pi03_categoria_inexistente_404(client, auth):
    r = client.post("/transactions/", headers=auth, json={"category_id": 9999, "type": "expense", "amount": 10})
    assert r.status_code == 404


def test_pi11_monto_invalido_422(client, auth, cat_gasto):
    for monto in (0, -5, 10**14):
        r = client.post("/transactions/", headers=auth, json={"category_id": cat_gasto, "type": "expense", "amount": monto})
        assert r.status_code == 422


def test_pi15_aislamiento_entre_usuarios(client, auth, auth_otro, cat_gasto):
    client.post("/transactions/", headers=auth, json={"category_id": cat_gasto, "type": "expense", "amount": 10})
    assert client.get("/transactions/", headers=auth_otro).json() == []


def test_pi14_editar_transaccion_con_categoria_ajena_404(client, auth, auth_otro, cat_gasto):
    ajena = client.post("/categories/", headers=auth_otro,
                        json={"name_cat": "Privada", "type": "expense"}).json()["category_id"]
    tid = client.post("/transactions/", headers=auth,
                      json={"category_id": cat_gasto, "type": "expense", "amount": 10}).json()["trans_id"]
    r = client.put(f"/transactions/{tid}", headers=auth,
                   json={"category_id": ajena, "type": "expense", "amount": 10})
    assert r.status_code == 404
    r = client.put(f"/transactions/{tid}", headers=auth,
                   json={"category_id": cat_gasto, "type": "expense", "amount": 25})
    assert r.status_code == 200 and r.json()["amount"] == 25


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


def test_editar_presupuesto_solo_cambia_campos_enviados(client, auth, cat_gasto):
    bid = _presupuesto(client, auth, cat_gasto).json()["budget_id"]
    r = client.put(f"/budgets/{bid}", headers=auth, json={"amount": 300000, "name": None})
    assert r.status_code == 200, r.text
    assert r.json()["amount"] == 300000
    assert r.json()["name"] == "Comida"
    assert client.put(f"/budgets/{bid}", headers=auth, json={"category_id": 9999}).status_code == 404


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
def test_pi12_d01_meta_pequena_sin_cuotas_negativas(client, auth):
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


def test_pi06_marcar_dias_y_progreso(client, auth):
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


def test_pi07_editar_meta_regenera_plan(client, auth):
    fin = (date.today() + timedelta(days=9)).isoformat()
    gid = client.post("/saving-goals/", headers=auth, json={"name": "A", "target_amount": 100000, "end_date": fin}).json()["goal_id"]
    r = client.put(f"/saving-goals/{gid}", headers=auth, json={"target_amount": 200000})
    assert sum(r.json()["daily_amounts"].values()) == 200000


def test_meta_ajena_404(client, auth, auth_otro):
    gid = client.post("/saving-goals/", headers=auth, json={"name": "A", "target_amount": 1000}).json()["goal_id"]
    assert client.post(f"/saving-goals/{gid}/toggle-day/1", headers=auth_otro).status_code == 404
    assert client.delete(f"/saving-goals/{gid}", headers=auth_otro).status_code == 404


# ── Eliminación en cascada (D-11) ─────────────────────────────────────────────
def test_pi13_d11_eliminar_cuenta_con_datos_asociados(client, auth, cat_gasto):
    client.post("/transactions/", headers=auth, json={"category_id": cat_gasto, "type": "expense", "amount": 10})
    client.post("/budgets/", headers=auth, json={"category_id": cat_gasto, "name": "x", "amount": 5, "period_type": "monthly", "month": date.today().month, "year": date.today().year})
    client.post("/saving-goals/", headers=auth, json={"name": "m", "target_amount": 1000})
    client.post("/categories/", headers=auth, json={"name_cat": "Propia", "type": "expense"})
    r = client.delete("/users/me", headers=auth)
    assert r.status_code == 204, r.text

def test_pi13_d11_eliminar_categoria_elimina_sus_presupuestos(client, auth):
    cid = client.post("/categories/", headers=auth, json={"name_cat": "Viajes", "type": "expense"}).json()["category_id"]
    client.post("/budgets/", headers=auth, json={"category_id": cid, "name": "x", "amount": 5, "period_type": "monthly", "month": date.today().month, "year": date.today().year})
    r = client.delete(f"/categories/{cid}", headers=auth)
    assert r.status_code == 204, r.text
    assert client.get("/budgets/", headers=auth).json() == []


# ── Perfil (RF19) ─────────────────────────────────────────────────────────────
def test_pi16_perfil_actualiza_datos_y_moneda(client, auth, auth_otro):
    r = client.put("/users/me", headers=auth, json={"username": "ana2", "email": "ana2@correo.com"})
    assert r.status_code == 200 and r.json()["username"] == "ana2"
    assert client.put("/users/me", headers=auth, json={"username": "x", "email": "beto@correo.com"}).status_code == 400
    assert client.put("/users/me/currency", headers=auth, json={"currency": "USD"}).json()["currency"] == "USD"
    assert client.get("/users/me", headers=auth).json()["email"] == "ana2@correo.com"


def test_pi16_cambio_de_contrasena_exige_la_actual(client, auth):
    malo = {"current_password": "incorrecta", "new_password": "NuevaClave1"}
    bueno = {"current_password": "Segura123", "new_password": "NuevaClave1"}
    assert client.put("/users/me/password", headers=auth, json=malo).status_code == 400
    assert client.put("/users/me/password", headers=auth, json=bueno).status_code == 200
    r = client.post("/auth/login", json={"email": "ana@correo.com", "password": "NuevaClave1"})
    assert r.status_code == 200


def test_pi16_foto_de_perfil(client, auth, tmp_path, monkeypatch):
    from app.routes import profile
    monkeypatch.setattr(profile, "UPLOAD_DIR", str(tmp_path))
    malo = client.post("/users/me/picture", headers=auth, files={"file": ("a.txt", b"hola", "text/plain")})
    assert malo.status_code == 400
    grande = client.post("/users/me/picture", headers=auth,
                         files={"file": ("a.png", b"0" * (3 * 1024 * 1024 + 1), "image/png")})
    assert grande.status_code == 400
    ok = client.post("/users/me/picture", headers=auth, files={"file": ("a.png", b"\x89PNG", "image/png")})
    assert ok.status_code == 200 and ok.json()["profile_pic"].endswith(".png")
    assert len(list(tmp_path.iterdir())) == 1
    assert client.delete("/users/me/picture", headers=auth).json()["profile_pic"] is None
    assert client.delete("/users/me/picture", headers=auth).status_code == 404


# ── Inicio de sesión con Google (RF02, CU06) ──────────────────────────────────
class _RespuestaGoogle:
    def __init__(self, status_code, datos=None):
        self.status_code, self._datos = status_code, datos or {}

    def json(self):
        return self._datos


def _simular_google(monkeypatch, status_code, datos=None):
    from app.routes import users
    monkeypatch.setattr(users.http_requests, "get", lambda *a, **k: _RespuestaGoogle(status_code, datos))


def test_pi17_google_crea_cuenta_y_devuelve_jwt(client, monkeypatch):
    _simular_google(monkeypatch, 200, {"email": "carla@gmail.com", "name": "Carla"})
    r = client.post("/auth/google", json={"access_token": "token-google"})
    assert r.status_code == 200, r.text
    assert r.json()["user"]["email"] == "carla@gmail.com"
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    assert client.get("/users/me", headers=headers).status_code == 200
    # segunda vez: reutiliza la cuenta existente
    assert client.post("/auth/google", json={"access_token": "token-google"}).json()["user"]["user_id"] == \
        r.json()["user"]["user_id"]


def test_pi17_google_token_invalido_o_sin_correo(client, monkeypatch):
    _simular_google(monkeypatch, 401)
    assert client.post("/auth/google", json={"access_token": "malo"}).status_code == 401
    _simular_google(monkeypatch, 200, {"name": "Sin correo"})
    assert client.post("/auth/google", json={"access_token": "x"}).status_code == 400


# ── Rutas de consulta y edición restantes ─────────────────────────────────────
def test_editar_categoria_propia(client, auth):
    cid = client.post("/categories/", headers=auth, json={"name_cat": "Ocio", "type": "expense"}).json()["category_id"]
    r = client.put(f"/categories/{cid}", headers=auth, json={"name_cat": "Cine", "icon": "🎬", "type": "expense"})
    assert r.status_code == 200 and r.json()["name_cat"] == "Cine"
    assert any(c["name_cat"] == "Cine" for c in client.get("/categories/", headers=auth).json())


def test_consultar_y_eliminar_meta(client, auth):
    gid = client.post("/saving-goals/", headers=auth, json={"name": "Bici", "target_amount": 3000}).json()["goal_id"]
    assert client.get(f"/saving-goals/{gid}", headers=auth).json()["progress"]["total_days"] == 31
    assert len(client.get("/saving-goals/", headers=auth).json()) == 1
    assert client.delete(f"/saving-goals/{gid}", headers=auth).status_code == 200
    assert client.get(f"/saving-goals/{gid}", headers=auth).status_code == 404

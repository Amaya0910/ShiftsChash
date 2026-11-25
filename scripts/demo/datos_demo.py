"""Carga datos ficticios en la API local para la demostración.

Usuario: demo@correo.com / Demo12345. Las fechas se calculan desde el día en que
se ejecuta, para que el resumen y los presupuestos del mes actual tengan datos.
Si el usuario ya tiene transacciones, no vuelve a cargar nada.
"""
import sys
from datetime import date, timedelta

import requests

API = "http://localhost:8000"
CRED = {"email": "demo@correo.com", "password": "Demo12345"}


def main() -> None:
    requests.post(f"{API}/auth/register", json={"username": "Usuario demo", **CRED}, timeout=30)
    token = requests.post(f"{API}/auth/login", json=CRED, timeout=30).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    if requests.get(f"{API}/transactions/", headers=headers, timeout=30).json():
        print("El usuario demo ya tiene datos; no se carga nada.")
        return

    def post(ruta, cuerpo):
        r = requests.post(f"{API}{ruta}", json=cuerpo, headers=headers, timeout=30)
        if r.status_code not in (200, 201):
            sys.exit(f"Error en {ruta}: {r.status_code} {r.text}")
        return r.json()

    hoy = date.today()

    def dia(n):  # n-ésimo día del mes actual, sin pasar de hoy
        return hoy.replace(day=min(n, hoy.day)).isoformat()

    cat = {n: post("/categories/", {"name_cat": n, "icon": i, "type": t})["category_id"]
           for n, i, t in [("Alimentación", "🍔", "expense"), ("Transporte", "🚌", "expense"),
                           ("Vivienda", "🏠", "expense"), ("Salario", "💼", "income")]}
    for c, t, monto, desc, d, rec in [
        ("Salario", "income", 2500000, "Salario del mes", dia(1), "monthly"),
        ("Vivienda", "expense", 800000, "Arriendo", dia(2), "monthly"),
        ("Alimentación", "expense", 320000, "Mercado", dia(5), None),
        ("Alimentación", "expense", 250000, "Restaurantes", dia(12), None),
        ("Alimentación", "expense", 130000, "Domicilios", dia(18), None),
        ("Transporte", "expense", 150000, "Recargas transporte", dia(10), None),
    ]:
        post("/transactions/", {"category_id": cat[c], "type": t, "amount": monto, "description": desc,
                                "trans_date": d, "is_recurring": rec is not None, "frequency": rec})
    for categoria, nombre, monto in [("Alimentación", "Comida del mes", 600000), ("Transporte", "Transporte", 400000)]:
        post("/budgets/", {"category_id": cat[categoria], "name": nombre, "amount": monto,
                           "period_type": "monthly", "month": hoy.month, "year": hoy.year})
    meta = post("/saving-goals/", {"name": "Fondo de emergencia", "target_amount": 1500000,
                                   "start_date": hoy.isoformat(), "end_date": (hoy + timedelta(days=29)).isoformat()})
    for n in (1, 2, 3):
        post(f"/saving-goals/{meta['goal_id']}/toggle-day/{n}", {})
    reto = post("/saving-goals/", {"name": "Reto pequeño", "target_amount": 1000,
                                   "start_date": hoy.isoformat(), "end_date": (hoy + timedelta(days=14)).isoformat()})
    print("Datos cargados. Cuotas del reto pequeño:", list(reto["daily_amounts"].values()))


if __name__ == "__main__":
    main()

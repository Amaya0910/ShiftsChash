"""Estimación de esfuerzo, tiempo y costo de ShiftCash (Cuarta parte).

Recalcula los seis modelos con los mismos datos del documento y los compara con
la duración real. Uso: python docs/scripts/estimacion.py
"""
import math

HORAS_PM = 160                 # horas por persona-mes
SEMANAS_MES = 52 / 12          # 4,33 semanas por mes
EQUIPO = 3                     # desarrolladores reales (Primera parte)
DURACION_REAL_MESES = 51 / (365 / 12)   # 21/04/2026 a 10/06/2026


# Método de clase para PF y COSMIC: 8 h por punto, jornadas de 8 h, 3 personas,
# meses de 20 días hábiles y un sueldo de 3 500 000 COP por persona al mes.
HORAS_POR_PUNTO = 8
HORAS_DIA = 8
DIAS_MES = 20
SUELDO_CLASE = 3_500_000


def metodo_clase(puntos: float) -> dict:
    """Horas = puntos × 8; días = horas / (8 h × 3 personas); meses = días / 20."""
    horas = puntos * HORAS_POR_PUNTO
    dias = horas / (HORAS_DIA * EQUIPO)
    return {"pm": horas / (HORAS_DIA * DIAS_MES), "meses": dias / DIAS_MES, "costo_pm": SUELDO_CLASE,
            "horas": horas, "dias": dias}


def calendario(pm: float) -> float:
    """Ecuación de calendario de COCOMO 81 orgánico: T = 2,5 · E^0,38."""
    return 2.5 * pm ** 0.38


# ── Puntos de función (IFPUG) ────────────────────────────────────────────────
def puntos_funcion() -> dict:
    conteo = {  # tipo: (cantidad, peso)
        "ILF baja": (5, 7), "EIF baja": (1, 5), "EI media": (6, 4), "EI baja": (16, 3),
        "EO media": (4, 5), "EO alta": (1, 7), "EQ baja": (4, 3),
    }
    pfna = sum(n * w for n, w in conteo.values())
    gsc = [4, 3, 2, 2, 2, 5, 4, 4, 2, 2, 2, 3, 3, 3]   # 14 características generales
    vaf = 0.65 + 0.01 * sum(gsc)
    pf = pfna * vaf
    clase = metodo_clase(pf)
    return {"tamano": f"{pf:.2f} PF", **clase,
            "detalle": f"PFNA={pfna}, VAF={vaf:.2f}, {clase['horas']:.0f} h, {clase['dias']:.1f} días"}


# ── Puntos de función COSMIC (ISO/IEC 19761) ─────────────────────────────────
# Movimientos de datos (E, X, R, W) de los 30 procesos funcionales (Tabla de COSMIC)
PROCESOS_COSMIC = [
    (1, 1, 1, 1), (1, 2, 1, 0), (2, 3, 1, 1), (1, 1, 1, 0), (1, 1, 1, 1), (1, 1, 1, 1),
    (1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 5), (1, 1, 1, 0), (1, 1, 1, 1),
    (1, 1, 1, 1), (1, 1, 2, 2), (1, 1, 1, 1), (1, 1, 2, 0), (1, 1, 2, 1), (1, 1, 1, 1),
    (1, 1, 1, 1), (1, 1, 3, 0), (1, 1, 2, 1), (1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 1, 0),
    (1, 1, 2, 1), (1, 1, 1, 1), (1, 1, 1, 1), (1, 1, 2, 0), (1, 1, 2, 0), (1, 0, 1, 1),
]


def puntos_cosmic() -> dict:
    e, x, r, w = (sum(p[i] for p in PROCESOS_COSMIC) for i in range(4))
    cfp = e + x + r + w
    clase = metodo_clase(cfp)
    return {"tamano": f"{cfp} CFP", **clase,
            "detalle": f"E={e}, X={x}, R={r}, W={w}, {clase['horas']:.0f} h, {clase['dias']:.1f} días"}


# ── Puntos de casos de uso (Karner) ──────────────────────────────────────────
def puntos_casos_uso() -> dict:
    uaw = 3 + 2 + 1                                     # Usuario, Google OAuth, programador
    uucw = 3 * 5 + 9 * 10 + 2 * 15                      # 14 casos de uso
    tf_valores = [3, 3, 3, 2, 1, 1, 3, 3, 4, 2, 1, 0, 1]
    tf_pesos = [2, 1, 1, 1, 1, 0.5, 0.5, 2, 1, 1, 1, 1, 1]
    ef_valores = [3, 2, 3, 4, 4, 3, 1, 1]
    ef_pesos = [1.5, 0.5, 1, 0.5, 1, 2, -1, -1]
    tcf = 0.6 + 0.01 * sum(v * p for v, p in zip(tf_valores, tf_pesos))
    ecf = 1.4 - 0.03 * sum(v * p for v, p in zip(ef_valores, ef_pesos))
    ucp = (uaw + uucw) * tcf * ecf
    return {"tamano": f"{ucp:.2f} PCU", "pm": ucp * 20 / HORAS_PM,
            "detalle": f"UUCP={uaw + uucw}, TCF={tcf:.2f}, ECF={ecf:.3f}"}


# ── Puntos de objeto (COCOMO II, composición de aplicaciones) ────────────────
def puntos_objeto() -> dict:
    po = 4 * 1 + 7 * 2 + 5 * 3 + 8 * 10                 # pantallas y componentes 3GL
    nop = po * (1 - 0.20)                               # 20 % de reúso
    return {"tamano": f"{nop:.1f} NOP", "pm": nop / 13, "detalle": f"PO={po}, PROD=13"}


# ── Puntos de historia ───────────────────────────────────────────────────────
HISTORIAS = [5, 5, 8, 3, 5, 5, 8, 5, 13, 8, 13, 5, 3, 2, 1]


def puntos_historia(velocidad=20, semanas_sprint=2) -> dict:
    ph = sum(HISTORIAS)
    sprints = ph / velocidad
    meses = sprints * semanas_sprint / SEMANAS_MES
    return {"tamano": f"{ph} PH", "pm": meses * EQUIPO, "meses": meses,
            "detalle": f"{sprints:.2f} sprints de {semanas_sprint} semanas a {velocidad} PH"}


# ── COCOMO II post-arquitectura ──────────────────────────────────────────────
def cocomo(ksloc=6.228) -> dict:
    sf = [3.72, 3.04, 4.24, 3.29, 4.68]                 # factores de escala nominales
    em = [0.91, 0.87, 1.10, 1.09, 1.09, 0.90, 0.93]     # DOCU, PVOL, APEX, PLEX, LTEX, TOOL, SITE
    e = 0.91 + 0.01 * sum(sf)
    pm = 2.94 * ksloc ** e * math.prod(em)
    tdev = 3.67 * pm ** (0.28 + 0.2 * (e - 0.91))
    return {"tamano": f"{ksloc:.3f} KSLOC", "pm": pm, "meses": tdev,
            "detalle": f"E={e:.4f}, EAF={math.prod(em):.3f}"}


# ── Presupuesto ──────────────────────────────────────────────────────────────
SMMLV_2026 = 1_750_905          # Decreto 1470 de 2025
SALARIO_BASE = 2.5 * SMMLV_2026  # el 65,6 % de los egresados TIC supera 2,5 SMMLV (OLE)
# Carga prestacional de ley (%): cesantías, intereses, prima, vacaciones, pensión,
# salud, ARL (riesgo I), caja de compensación, ICBF y SENA
PRESTACIONES = [8.33, 1, 8.33, 4.17, 12, 8.5, 0.522, 4, 3, 2]
COSTO_PM = SALARIO_BASE * (1 + sum(PRESTACIONES) / 100)
POTENCIA_KW = 0.065                           # consumo estimado de un portátil (65 W)
TARIFA_KWH = 879                              # costo promedio en la zona de Afinia (COP/kWh)
IMPREVISTOS = 0.10
VALOR_PORTATIL = 2_000_000       # portátil de gama media (estimación; Portafolio)
VIDA_UTIL_MESES = 60             # equipo de cómputo: 20 % anual (art. 137 del Estatuto Tributario)
INTERNET_MES = 80_000            # plan de fibra promedio en Colombia, abril de 2026
HORAS_SEMANA = 15                # dedicación estimada de cada estudiante al proyecto
RENDER_STARTER_USD = 7           # plan de pago más bajo de Render, por mes


def presupuesto(pm: float, meses: float) -> dict:
    """Presupuesto desglosado con valores estimados."""
    rubros = {
        "Talento humano": pm * COSTO_PM,
        "Energía eléctrica": pm * HORAS_PM * POTENCIA_KW * TARIFA_KWH,
        "Equipos (depreciación)": EQUIPO * VALOR_PORTATIL / VIDA_UTIL_MESES * meses,
        "Internet": EQUIPO * INTERNET_MES * meses,
        "Hosting (Vercel Hobby, Render Free, Supabase Free)": 0,
        "Dominio (subdominio vercel.app)": 0,
        "Licencias y herramientas (código abierto y planes gratuitos)": 0,
    }
    subtotal = sum(rubros.values())
    rubros["Imprevistos (10 %)"] = subtotal * IMPREVISTOS
    rubros["Total"] = subtotal * (1 + IMPREVISTOS)
    return rubros


def main() -> None:
    modelos = {
        "Puntos de función": puntos_funcion(),
        "Puntos de función COSMIC": puntos_cosmic(),
        "Puntos de casos de uso": puntos_casos_uso(),
        "Puntos de objeto": puntos_objeto(),
        "Puntos de historia": puntos_historia(),
        "COCOMO II": cocomo(),
    }
    print(f"PF y COSMIC (método de clase): {HORAS_POR_PUNTO} h por punto, jornadas de {HORAS_DIA} h, {EQUIPO} personas, "
          f"{DIAS_MES} días por mes y sueldo de {SUELDO_CLASE:,.0f} COP")
    print(f"Costo de una persona-mes: {COSTO_PM:,.0f} COP (salario {SALARIO_BASE:,.0f} "
          f"+ {sum(PRESTACIONES):.2f} % de prestaciones)\n")
    print(f"{'Modelo':24} {'Tamaño':>13} {'PM':>7} {'Meses':>6} {'Personas':>8} {'Talento (COP)':>15}  Detalle")
    for nombre, m in modelos.items():
        meses = m.get("meses") or calendario(m["pm"])
        m["meses"] = meses
        print(f"{nombre:24} {m['tamano']:>13} {m['pm']:7.2f} {meses:6.2f} {m['pm'] / meses:8.2f} "
              f"{m['pm'] * m.get('costo_pm', COSTO_PM):15,.0f}  {m['detalle']}")

    elegido = modelos["Puntos de historia"]
    real_pm = DURACION_REAL_MESES * SEMANAS_MES * HORAS_SEMANA * EQUIPO / HORAS_PM
    for titulo, pm, meses in (("estimado con puntos de historia", elegido["pm"], elegido["meses"]),
                              ("del proyecto real (esfuerzo estimado)", real_pm, DURACION_REAL_MESES)):
        print(f"\nPresupuesto {titulo}: {pm:.2f} PM en {meses:.2f} meses")
        for rubro, valor in presupuesto(pm, meses).items():
            print(f"  {rubro:62} {valor:15,.0f}")

    sprints_reales = DURACION_REAL_MESES * SEMANAS_MES / 2
    print(f"\nDuración real: {DURACION_REAL_MESES:.2f} meses con {EQUIPO} personas "
          f"(cota superior de esfuerzo: {DURACION_REAL_MESES * EQUIPO:.2f} PM a tiempo completo)")
    print(f"Esfuerzo real estimado: {HORAS_SEMANA} h/semana × {EQUIPO} personas × "
          f"{DURACION_REAL_MESES * SEMANAS_MES:.1f} semanas = {real_pm * HORAS_PM:.0f} h = {real_pm:.2f} PM")
    print(f"Costo real desembolsado: 0 COP (equipos e internet propios; planes gratuitos)")
    print(f"Plan de pago de Render para evitar la suspensión (D-09): {RENDER_STARTER_USD} USD/mes")
    print(f"Velocidad real del equipo: {sum(HISTORIAS) / sprints_reales:.1f} PH por sprint de 2 semanas "
          f"({sprints_reales:.2f} sprints)")


if __name__ == "__main__":
    main()

"""Genera los diagramas complementarios de la documentación de ShiftCash.

Uso:  python docs/diagramas/generar_diagramas.py
Requiere matplotlib. Las imágenes quedan en la misma carpeta.
"""
import os
from datetime import date

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.dates as mdates  # noqa: E402
from matplotlib.patches import Ellipse, FancyBboxPatch, Rectangle  # noqa: E402

OUT = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = "DejaVu Sans"
AZUL = "#1f4e79"
GRIS = "#444444"


def guardar(fig, nombre):
    fig.savefig(os.path.join(OUT, nombre), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def flecha(ax, x1, y1, x2, y2, estilo="-|>", ls="-", color=GRIS, lw=1.0, texto=None, rad=0.0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=estilo, linestyle=ls, color=color, lw=lw,
                                shrinkA=0, shrinkB=0, connectionstyle=f"arc3,rad={rad}"))
    if texto:
        ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, texto, fontsize=7, ha="center", color=color,
                style="italic", bbox=dict(fc="white", ec="none", pad=0.5))


def actor(ax, x, y, nombre):
    ax.add_patch(plt.Circle((x, y + 0.55), 0.15, fill=False, lw=1.3))
    ax.plot([x, x], [y + 0.4, y - 0.05], color="black", lw=1.3)
    ax.plot([x - 0.25, x + 0.25], [y + 0.25, y + 0.25], color="black", lw=1.3)
    ax.plot([x, x - 0.2], [y - 0.05, y - 0.4], color="black", lw=1.3)
    ax.plot([x, x + 0.2], [y - 0.05, y - 0.4], color="black", lw=1.3)
    ax.text(x, y - 0.65, nombre, ha="center", va="top", fontsize=8.5, weight="bold")


# ── 1. Diagrama general de casos de uso ──────────────────────────────────────
def _borde(cx, cy, w, h, tx, ty):
    """Punto del borde de la elipse (cx, cy, w, h) en dirección a (tx, ty)."""
    import math
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    t = 1 / math.sqrt((dx / (w / 2)) ** 2 + (dy / (h / 2)) ** 2)
    return cx + dx * t, cy + dy * t


def casos_de_uso():
    fig, ax = plt.subplots(figsize=(14, 11))
    ax.set_xlim(0, 14)
    ax.set_ylim(-0.4, 11.6)
    ax.axis("off")
    ax.add_patch(Rectangle((2.3, 0.1), 9.6, 11.2, fill=False, lw=1.5))
    ax.text(7.1, 10.95, "Sistema ShiftCash", ha="center", fontsize=12, weight="bold")

    W, H = 2.2, 0.72
    cus = {
        "CU04": (3.5, 10.2, "CU04 Registrarse"),
        "CU05": (4.4, 9.2, "CU05 Iniciar sesión"),
        "CU14": (5.2, 8.2, "CU14 Gestionar perfil\ny preferencias"),
        "CU09": (5.0, 2.6, "CU09 Ver resumen\ny alertas"),
        "CU10": (4.4, 1.6, "CU10 Ver gráficas"),
        "CU11": (3.5, 0.6, "CU11 Gestionar\ncategorías"),
        "CU01": (7.4, 7.4, "CU01 Registrar\ntransacción"),
        "CU07": (7.4, 6.4, "CU07 Editar o eliminar\ntransacción"),
        "CU08": (7.4, 5.4, "CU08 Consultar\nhistorial"),
        "CU02": (7.4, 4.2, "CU02 Gestionar\npresupuesto"),
        "CU03": (7.4, 2.9, "CU03 Gestionar\nmeta de ahorro"),
        "CU06": (10.4, 9.2, "CU06 Iniciar sesión\ncon Google"),
        "CU13": (10.4, 7.4, "CU13 Generar transac-\nciones recurrentes"),
        "INC1": (10.4, 5.9, "Seleccionar\ncategoría"),
        "INC2": (10.4, 4.2, "Calcular gasto\nejecutado"),
        "INC3": (10.4, 2.9, "Generar plan\ndiario"),
        "CU12": (10.4, 1.5, "CU12 Marcar día\nahorrado"),
    }
    for k, (x, y, t) in cus.items():
        aux = k.startswith("INC")
        ax.add_patch(Ellipse((x, y), W, H, fc="#f3f6fa" if not aux else "#fbfbfb",
                             ec=AZUL if not aux else GRIS, lw=1.2, ls="-" if not aux else "--"))
        ax.text(x, y, t, ha="center", va="center", fontsize=7.6)

    actor(ax, 1.0, 5.4, "Usuario")
    actor(ax, 13.1, 9.0, "Google OAuth\n(sistema externo)")
    actor(ax, 13.1, 7.0, "Programador de\ntareas (tiempo)")

    def linea_actor(ax_x, ax_y, k):
        x, y, _ = cus[k]
        ex, ey = _borde(x, y, W, H, ax_x, ax_y)
        ax.plot([ax_x, ex], [ax_y, ey], color=GRIS, lw=0.8)

    for k in ["CU04", "CU05", "CU14", "CU09", "CU10", "CU11", "CU01", "CU07", "CU08", "CU02", "CU03"]:
        linea_actor(1.35, 5.5, k)
    linea_actor(12.75, 9.1, "CU06")
    linea_actor(12.75, 7.1, "CU13")

    def dep(a, b, tipo):
        xa, ya, _ = cus[a]
        xb, yb, _ = cus[b]
        x1, y1 = _borde(xa, ya, W, H, xb, yb)
        x2, y2 = _borde(xb, yb, W, H, xa, ya)
        flecha(ax, x1, y1, x2, y2, estilo="->", ls="--", texto=f"«{tipo}»")

    dep("CU01", "INC1", "include")
    dep("CU02", "INC1", "include")
    dep("CU02", "INC2", "include")
    dep("CU03", "INC3", "include")
    dep("CU12", "CU03", "extend")
    dep("CU13", "CU01", "extend")
    dep("CU06", "CU05", "extend")
    ax.text(7.1, -0.2, "Precondición de CU01–CU03 y CU07–CU14: usuario autenticado (CU05 o CU06). "
            "CU06 y CU12 heredan el actor Usuario del caso base que extienden.",
            ha="center", fontsize=7.5, style="italic", color=GRIS)
    guardar(fig, "cu_general.png")


# ── 2. Diagrama de clases de la implementación ──────────────────────────────
def caja(ax, x, y, w, titulo, attrs, metodos, estereotipo=None, color="#eef3f8"):
    lh = 0.27
    h_t = 0.55 if estereotipo else 0.38
    h_a = max(1, len(attrs)) * lh + 0.1
    h_m = max(1, len(metodos)) * lh + 0.1
    h = h_t + h_a + h_m
    ax.add_patch(Rectangle((x, y - h), w, h, fc="white", ec="black", lw=1.1))
    ax.add_patch(Rectangle((x, y - h_t), w, h_t, fc=color, ec="black", lw=1.1))
    if estereotipo:
        ax.text(x + w / 2, y - 0.17, f"«{estereotipo}»", ha="center", va="center", fontsize=6.5, style="italic")
        ax.text(x + w / 2, y - 0.4, titulo, ha="center", va="center", fontsize=8.5, weight="bold")
    else:
        ax.text(x + w / 2, y - h_t / 2, titulo, ha="center", va="center", fontsize=8.5, weight="bold")
    yy = y - h_t - 0.05
    for a in attrs:
        ax.text(x + 0.08, yy - lh / 2, a, va="center", fontsize=6.6, family="DejaVu Sans Mono")
        yy -= lh
    ax.plot([x, x + w], [y - h_t - h_a] * 2, color="black", lw=1)
    yy = y - h_t - h_a - 0.05
    for m in metodos:
        ax.text(x + 0.08, yy - lh / 2, m, va="center", fontsize=6.6, family="DejaVu Sans Mono")
        yy -= lh
    return (x, y, w, h)


def clases():
    fig, ax = plt.subplots(figsize=(20, 14))
    ax.set_xlim(0, 30)
    ax.set_ylim(-1, 21)
    ax.axis("off")
    ax.text(15, 20.6, "Diagrama de clases de la implementación (backend, commit con correcciones)",
            ha="center", fontsize=13, weight="bold")

    # Paquete models (entidades ORM)
    ax.add_patch(Rectangle((0.3, 6.6), 18.6, 13.6, fill=False, ls="--", lw=1, ec=AZUL))
    ax.text(0.5, 19.95, "app.models  (entidades · SQLAlchemy)", fontsize=9, color=AZUL, weight="bold")
    ax.text(9.6, 19.3, "Todas las entidades heredan de Base = declarative_base()  (generalización omitida por claridad)",
            fontsize=7.5, style="italic", ha="center", color="#555555",
            bbox=dict(fc="#f7f7f7", ec="#999999", lw=0.6))
    user = caja(ax, 0.7, 17.3, 4.4, "User", [
        "+user_id: Integer «PK»", "+username: String(25)", "+email: String(150) «UQ»",
        "+password: String(255)", "+profile_pic: String(150)", "+currency: String(10)='COP'",
        "+created_at: TIMESTAMP"], [
        "+categories: list[Category]", "+budgets: list[Budget]",
        "+transactions: list[Transaction]", "+saving_goals: list[SavingGoal]"], "entity")
    cat = caja(ax, 7.0, 17.3, 4.3, "Category", [
        "+category_id: Integer «PK»", "+user_id: Integer «FK» NULL", "+name_cat: String(25)",
        "+icon: String(150)", "+type: String(10)", "+is_default: SmallInteger"], [
        "+user: User", "+budgets: list[Budget]"], "entity")
    bud = caja(ax, 13.2, 17.3, 5.3, "Budget", [
        "+budget_id: Integer «PK»", "+user_id: Integer «FK»", "+category_id: Integer «FK»",
        "+name: String(100)", "+amount: Numeric(15,2)", "+period_type: String(10)",
        "+month, year: SmallInteger", "+start_date, end_date: Date", "+is_permanent: Boolean"], [
        "+user: User", "+category: Category"], "entity")
    tra = caja(ax, 7.0, 12.4, 5.2, "Transaction", [
        "+trans_id: Integer «PK»", "+user_id: Integer «FK»",
        "+category_id: Integer «FK» RESTRICT", "+type: String(15)", "+amount: Numeric(15,2)",
        "+description: String(250)", "+trans_date: Date", "+is_recurring: Boolean",
        "+frequency: String(15)"], ["+user: User", "+category: Category"], "entity")
    sav = caja(ax, 0.7, 11.6, 5.0, "SavingGoal", [
        "+goal_id: Integer «PK»", "+user_id: Integer «FK»", "+name: String(100)",
        "+target_amount: Numeric(15,2)", "+start_date, end_date: Date", "+image_url: Text",
        "+completed_days: JSON (list[int])", "+daily_amounts: JSON (dict[str,float])",
        "+created_at: TIMESTAMP"], ["+user: User"], "entity")

    def rel(puntos, diamante=None, m1=None, m2=None, texto="", pos_texto=None):
        xs, ys = zip(*puntos)
        ax.plot(xs, ys, color="black", lw=1)
        if diamante:
            ax.plot(xs[0], ys[0], marker="D", ms=7, mec="black",
                    mfc="black" if diamante == "lleno" else "white", zorder=5)
        for m in (m1, m2):
            if m:
                t, x, y, ha = m
                ax.text(x, y, t, fontsize=7.5, ha=ha, va="center")
        if texto:
            px, py = pos_texto
            ax.text(px, py, texto, fontsize=7, style="italic", ha="center",
                    bbox=dict(fc="white", ec="none", pad=0.3))

    u_bot = user[1] - user[3]
    c_bot = cat[1] - cat[3]
    rel([(4.4, 17.3), (4.4, 18.4), (15.8, 18.4), (15.8, 17.3)], "lleno",
        ("1", 4.55, 17.5, "left"), ("0..*", 15.95, 17.5, "left"), "planifica (CASCADE)", (10.1, 18.4))
    rel([(5.1, 16.0), (7.0, 16.0)], "vacio", ("1", 5.25, 16.2, "left"), ("0..*", 6.9, 16.2, "right"),
        "posee", (6.05, 15.75))
    rel([(5.1, 14.4), (7.0, 11.4)], "lleno", ("1", 5.25, 14.6, "left"), ("0..*", 6.9, 11.15, "right"),
        "registra\n(CASCADE)", (6.35, 13.1))
    rel([(2.9, u_bot), (2.9, sav[1])], "lleno", ("1", 3.05, u_bot - 0.3, "left"),
        ("0..*", 3.05, sav[1] + 0.2, "left"), "persigue (CASCADE)", (2.9, (u_bot + sav[1]) / 2))
    rel([(9.2, c_bot), (9.2, 12.4)], None, ("1", 9.35, c_bot - 0.2, "left"), ("0..*", 9.35, 12.6, "left"),
        "clasifica (RESTRICT)", (10.2, (c_bot + 12.4) / 2))
    rel([(13.2, 15.2), (11.3, 15.2)], None, ("0..*", 13.1, 15.4, "right"), ("1", 11.4, 15.4, "left"),
        "limita", (12.25, 14.95))

    # Paquete schemas
    ax.add_patch(Rectangle((19.3, 6.6), 10.4, 13.6, fill=False, ls="--", lw=1, ec="#7a4e1f"))
    ax.text(19.5, 19.95, "app.schemas  (DTO · Pydantic BaseModel)", fontsize=9, color="#7a4e1f", weight="bold")
    s_b = caja(ax, 19.6, 19.5, 4.9, "BudgetBase", [
        "+category_id: int", "+name: str", "+amount: float", "+period_type: str",
        "+month, year: int | None", "+start_date, end_date: date|None", "+is_permanent: bool"], [
        "+amount_must_be_positive(v)", "+period_type_must_be_valid(v)",
        "+month_must_be_valid(v)", "+year_must_be_valid(v)"], color="#f8f0e6")
    caja(ax, 19.6, 19.5 - s_b[3] - 0.5, 2.6, "BudgetCreate", [], ["+unique_requires_dates()"], color="#f8f0e6")
    caja(ax, 22.4, 19.5 - s_b[3] - 0.5, 2.1, "BudgetOut", ["+budget_id: int", "+spent: float",
                                                          "+percentage: float"], [], color="#f8f0e6")
    yb = 19.5 - s_b[3] - 0.5
    flecha(ax, 20.9, yb, 20.9, 19.5 - s_b[3], color="black")
    flecha(ax, 23.45, yb, 23.45, 19.5 - s_b[3], color="black")
    caja(ax, 24.9, 19.5, 4.6, "TransactionCreate", [
        "+category_id: int", "+type: str", "+amount: float", "+trans_date: date|None",
        "+is_recurring: bool", "+frequency: str|None"], ["+amount_must_be_positive(v)",
                                                         "+type_must_be_valid(v)"], color="#f8f0e6")
    caja(ax, 24.9, 15.3, 4.6, "SavingGoalCreate", [
        "+name: str", "+target_amount: float", "+start_date: date|None", "+end_date: date|None",
        "+image_url: str|None"], ["+amount_must_be_positive(v)", "+name_not_empty(v)",
                                  "+end_date_must_be_future(v)", "+start_before_end()"], color="#f8f0e6")
    ax.text(19.6, 11.2, "Otros DTO del paquete (mismo patrón):\nUserCreate, UserLogin, UserOut, Token,\n"
            "TokenWithUser, GoogleAuthRequest, UserUpdate,\nPasswordUpdate, CurrencyUpdate, CategoryOut,\n"
            "CategoryCreate, CategoryUpdate, TransactionOut,\nBudgetUpdate, SavingGoalUpdate, SavingGoalOut",
            fontsize=7.3, va="top", bbox=dict(fc="#fffaf3", ec="#7a4e1f", lw=0.6))
    ax.text(25.0, 9.9, "Funciones de validación del módulo:\n_validar_monto(v)  · MAX_AMOUNT\n"
            "_validar_mes(v)\n_validar_anio(v)", fontsize=7.3, va="top", family="DejaVu Sans Mono",
            bbox=dict(fc="#fffaf3", ec="#7a4e1f", lw=0.6))

    # Capa de servicios (routers)
    ax.add_patch(Rectangle((0.3, -0.8), 29.4, 7.0, fill=False, ls="--", lw=1, ec="#2e6b30"))
    ax.text(0.5, 5.95, "app.routes / app.auth / app.scheduler  (servicios · FastAPI APIRouter)",
            fontsize=9, color="#2e6b30", weight="bold")
    g = "#eaf4ea"
    caja(ax, 0.6, 5.6, 4.6, "routes.transactions", ["+router: APIRouter('/transactions')"], [
        "+get_categories()", "+create_transaction(t, user, db)", "+get_transactions()",
        "+update_transaction(id, t)", "+delete_transaction(id)"], "module", g)
    caja(ax, 5.5, 5.6, 4.6, "routes.budgets", ["+router: APIRouter('/budgets')"], [
        "+get_date_range(b): tuple[date,date]", "+calculate_spent(b, db, u): float",
        "+get_budgets()", "+create_budget(data)", "+update_budget(id, data)",
        "+delete_budget(id)"], "module", g)
    caja(ax, 10.4, 5.6, 5.4, "routes.savings", ["+CURRENCY_CONFIG: dict", "+router: APIRouter('/saving-goals')"], [
        "+round_to_unit(v, unit): float", "+generate_daily_amounts(...): dict",
        "+calculate_progress(...): dict", "+create/update/delete_saving_goal()",
        "+toggle_day(goal_id, day_number)"], "module", g)
    caja(ax, 16.1, 5.6, 4.3, "routes.categories", ["+router: APIRouter('/categories')"], [
        "+get_categories()", "+create_category(c)", "+update_category(id, c)",
        "+delete_category(id)  [409 si en uso]"], "module", g)
    caja(ax, 20.7, 5.6, 4.3, "routes.users / profile", ["+router: '/auth', '/users'"], [
        "+register(u)", "+login(cred)", "+google_auth(body)", "+get_me() / update_me()",
        "+update_password/currency()", "+upload/delete_picture()", "+delete_me()"], "module", g)
    caja(ax, 25.3, 5.6, 4.2, "auth", ["+SECRET_KEY, ALGORITHM", "+oauth2_scheme"], [
        "+hash_password(p): str", "+verify_password(p, h): bool", "+create_access_token(d)",
        "+get_current_user(token, db)"], "module", g)
    caja(ax, 25.3, 2.0, 4.2, "scheduler", ["+scheduler: BackgroundScheduler"], [
        "+_toca_hoy(t, hoy): bool", "+registrar_recurrentes()"], "module", g)
    ax.text(15.0, -0.55, "Dependencias «use»: cada router usa app.schemas para validar la entrada/salida, "
            "app.models + database.get_db para persistir y auth.get_current_user para autorizar.",
            ha="center", fontsize=8, style="italic", color="#2e6b30")
    for x in (2.9, 7.8, 13.1, 18.2, 22.8):
        flecha(ax, x, 6.25, x, 6.75, estilo="->", ls="--", color="#2e6b30")
    guardar(fig, "clases_implementacion.png")


# ── 3. Árbol de problemas ────────────────────────────────────────────────────
def arbol():
    fig, ax = plt.subplots(figsize=(13, 7.5))
    ax.set_xlim(0, 13)
    ax.set_ylim(-0.5, 7.5)
    ax.axis("off")

    def nodo(x, y, t, fc, w=2.7, h=0.95):
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.05",
                                    fc=fc, ec=GRIS, lw=1))
        ax.text(x, y, t, ha="center", va="center", fontsize=8, wrap=True)

    ax.text(0.2, 6.9, "EFECTOS", fontsize=10, weight="bold", color="#8b1a1a")
    ax.text(0.2, 0.55, "CAUSAS", fontsize=10, weight="bold", color=AZUL)
    efectos = ["Gastos «hormiga» y\nsobregiros no detectados", "Endeudamiento y falta\nde dinero a fin de mes",
               "Metas de ahorro\nabandonadas", "Decisiones financieras\nsin información"]
    causas = ["Registro manual (cuaderno,\nExcel) lento y con errores", "No hay límites de gasto\npor categoría ni alertas",
              "Ahorro sin plan diario\nni seguimiento visible", "Movimientos recurrentes\nque se olvidan registrar"]
    xs = [1.9, 5.0, 8.1, 11.2]
    for x, t in zip(xs, efectos):
        nodo(x, 6.1, t, "#fbe9e9")
        flecha(ax, 6.5, 4.25, x, 5.62, estilo="-|>")
    nodo(6.5, 3.75, "PROBLEMA CENTRAL\nLas personas no controlan de forma sistemática sus ingresos,\n"
         "gastos, presupuestos y metas de ahorro", "#fff4cc", w=7.6, h=1.0)
    for x, t in zip(xs, causas):
        nodo(x, 1.35, t, "#e8f0fa")
        flecha(ax, x, 1.83, 6.5, 3.25, estilo="-|>")
    ax.text(6.5, -0.3, "ShiftCash ataca las cuatro causas: registro guiado (CU01), presupuestos con alerta (CU02, CU09), "
            "plan de ahorro diario (CU03) y recurrencias automáticas (CU13).", ha="center", fontsize=7.8, style="italic")
    guardar(fig, "arbol_problema.png")


# ── 4. Cronograma ────────────────────────────────────────────────────────────
TAREAS = [
    # (fase, actividad, inicio, fin, responsable)
    ("Sprint 0", "Planteamiento del problema y requisitos", date(2026, 8, 3), date(2026, 8, 14), "Ambos"),
    ("Sprint 1", "Arquitectura, BD, autenticación y categorías", date(2026, 8, 13), date(2026, 8, 28), "Ambos"),
    ("Sprint 2", "Transacciones, historial y recurrencias", date(2026, 8, 31), date(2026, 9, 11), "Ambos"),
    ("Sprint 3", "Presupuestos, resumen y gráficas", date(2026, 9, 14), date(2026, 9, 25), "Ambos"),
    ("Sprint 4", "Metas de ahorro, perfil y tema", date(2026, 9, 28), date(2026, 10, 9), "Ambos"),
    ("Sprint 5", "Despliegue Vercel/Render y CI", date(2026, 10, 12), date(2026, 10, 17), "Ambos"),
    ("Calidad", "Modelos UML y pruebas (unit., integ., sistema)", date(2026, 10, 12), date(2026, 10, 25), "Ambos"),
    ("Calidad", "Métricas y estimación", date(2026, 10, 19), date(2026, 10, 25), "Ambos"),
    ("Cierre", "Corrección de defectos y pruebas automatizadas", date(2026, 11, 16), date(2026, 11, 22), "Ambos"),
    ("Cierre", "Aceptación con usuarios y documento final", date(2026, 11, 23), date(2026, 11, 29), "Ambos"),
    ("Cierre", "Presentación y sustentación", date(2026, 11, 30), date(2026, 12, 4), "Ambos"),
]


def cronograma():
    fig, ax = plt.subplots(figsize=(12, 5.2))
    colores = {"Sprint 0": "#9fb8d6", "Sprint 1": AZUL, "Sprint 2": AZUL, "Sprint 3": AZUL, "Sprint 4": AZUL,
               "Sprint 5": AZUL, "Calidad": "#2e6b30", "Cierre": "#b5651d"}
    for i, (f, a, ini, fin, _) in enumerate(reversed(TAREAS)):
        ax.barh(i, (fin - ini).days + 1, left=mdates.date2num(ini), color=colores[f], height=0.6)
        ax.text(mdates.date2num(fin) + 1.5, i, f"{(fin - ini).days + 1} d", va="center", fontsize=7)
    ax.set_yticks(range(len(TAREAS)))
    ax.set_yticklabels([f"{f} · {a}" for f, a, *_ in reversed(TAREAS)], fontsize=8)
    ax.xaxis_date()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
    ax.grid(axis="x", ls=":", alpha=0.6)
    ax.set_title("Cronograma del proyecto ShiftCash (agosto – diciembre de 2026)", fontsize=11, weight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    guardar(fig, "cronograma.png")


if __name__ == "__main__":
    casos_de_uso()
    clases()
    arbol()
    cronograma()
    print("Diagramas generados en", OUT)

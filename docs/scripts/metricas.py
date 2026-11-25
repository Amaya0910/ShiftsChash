"""Métricas internas de ShiftCash (Apéndice E).

Tres mediciones, todas sobre el código fuente y sin ejecutarlo:

  complejidad  Complejidad ciclomática de McCabe por función y WMC por módulo.
  tamano       Líneas físicas, en blanco, de comentario y de código por lenguaje.
  frontend     Puntos de decisión por componente JSX (aproximación de McCabe).
  ck           Suite de Chidamber y Kemerer (WMC, DIT, NOC, CBO, RFC y LCOM) para
               las clases del backend y para cada módulo tratado como una clase.

Uso (desde la raíz del repositorio):
    python docs/scripts/metricas.py complejidad [--raiz backend/app] [--umbral 10]
    python docs/scripts/metricas.py tamano [--raiz .]
    python docs/scripts/metricas.py frontend [--raiz frontend/src] [--top 8]
    python docs/scripts/metricas.py ck [--raiz backend/app]
"""
import argparse
import ast
import itertools
import pathlib
import re
import subprocess

DECISIONES = (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.IfExp, ast.comprehension)
FUNCIONES = (ast.FunctionDef, ast.AsyncFunctionDef)

# Lenguaje por extensión y marcadores de comentario de línea y de bloque
LENGUAJES = {
    ".py": ("Python", "#", ('"""', '"""')),
    ".jsx": ("JSX", "//", ("/*", "*/")),
    ".js": ("JavaScript", "//", ("/*", "*/")),
    ".css": ("CSS", None, ("/*", "*/")),
    ".html": ("HTML", None, ("<!--", "-->")),
    ".json": ("JSON", None, None),
    ".yml": ("YAML", "#", None),
    ".jmx": ("XML (JMeter)", None, ("<!--", "-->")),
}
EXCLUIDOS = ("docs/", "dist/", "node_modules/", "package-lock.json", "scripts/")
PRUEBAS = ("backend/tests/", "tests/", "cypress/", "cypress.config.js")


# ── Complejidad ciclomática ───────────────────────────────────────────────────
def complejidad(funcion: ast.AST) -> int:
    """Complejidad de McCabe: 1 + puntos de decisión + operandos booleanos extra."""
    total = 1
    for nodo in ast.walk(funcion):
        if isinstance(nodo, DECISIONES):
            total += 1
        elif isinstance(nodo, ast.BoolOp):
            total += len(nodo.values) - 1
    return total


def modulos(raiz: pathlib.Path):
    for ruta in sorted(raiz.rglob("*.py")):
        yield ruta, ast.parse(ruta.read_text(encoding="utf-8"))


def cmd_complejidad(args) -> None:
    criticas = []
    for ruta, arbol in modulos(pathlib.Path(args.raiz)):
        medidas = [(f.name, complejidad(f)) for f in ast.walk(arbol) if isinstance(f, FUNCIONES)]
        if not medidas:
            continue
        print(f"{ruta.as_posix():45} WMC={sum(c for _, c in medidas):3}  max={max(c for _, c in medidas):2}")
        criticas += [(ruta.as_posix(), n, c) for n, c in medidas if c > args.umbral]
    print(f"\nFunciones con complejidad > {args.umbral}: {len(criticas)}")
    for ruta, nombre, c in criticas:
        print(f"  {ruta}:{nombre} = {c}")


# ── Tamaño ────────────────────────────────────────────────────────────────────
def archivos_del_repositorio(raiz: pathlib.Path, incluir_pruebas: bool = True) -> list:
    """Archivos versionados o nuevos no ignorados por git, sin documentación ni binarios."""
    salida = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                            cwd=raiz, capture_output=True, text=True, check=True).stdout
    return [raiz / r for r in salida.splitlines()
            if pathlib.Path(r).suffix in LENGUAJES and not r.startswith(EXCLUIDOS) and (raiz / r).exists()
            and (incluir_pruebas or not r.startswith(PRUEBAS))]


def contar_lineas(ruta: pathlib.Path) -> tuple:
    """Devuelve (físicas, en blanco, comentario, código)."""
    _, linea, bloque = LENGUAJES[ruta.suffix]
    blancas = comentarios = 0
    dentro = False
    lineas = ruta.read_text(encoding="utf-8", errors="replace").splitlines()
    for texto in (l.strip() for l in lineas):
        if not texto:
            blancas += 1
        elif dentro:
            comentarios += 1
            dentro = not texto.endswith(bloque[1])
        elif bloque and texto.startswith(bloque[0]):
            comentarios += 1
            dentro = not (texto.endswith(bloque[1]) and len(texto) > len(bloque[0]))
        elif linea and texto.startswith(linea):
            comentarios += 1
    return len(lineas), blancas, comentarios, len(lineas) - blancas - comentarios


def cmd_tamano(args) -> None:
    totales = {}
    for ruta in archivos_del_repositorio(pathlib.Path(args.raiz).resolve(), not args.sin_pruebas):
        lenguaje = LENGUAJES[ruta.suffix][0]
        acumulado = totales.setdefault(lenguaje, [0, 0, 0, 0, 0])
        acumulado[0] += 1
        for i, valor in enumerate(contar_lineas(ruta), start=1):
            acumulado[i] += valor
    print(f"{'Lenguaje':14} {'Archivos':>8} {'Físicas':>8} {'Blanco':>8} {'Coment.':>8} {'Código':>8}")
    suma = [0] * 5
    for lenguaje, fila in sorted(totales.items(), key=lambda x: -x[1][4]):
        print(f"{lenguaje:14} " + " ".join(f"{v:8}" for v in fila))
        suma = [a + b for a, b in zip(suma, fila)]
    print(f"{'Total':14} " + " ".join(f"{v:8}" for v in suma))


# ── Complejidad aproximada del frontend ───────────────────────────────────────
DECISION_JS = re.compile(r"\bif\b|\bfor\b|\bwhile\b|\bcase\b|\bcatch\b|\?(?![.?])|&&|\|\|")
FUNCION_JS = re.compile(r"\bfunction\b|=>")


def cmd_frontend(args) -> None:
    filas = []
    for ruta in pathlib.Path(args.raiz).rglob("*.jsx"):
        codigo = re.sub(r"//.*|/\*[\s\S]*?\*/", "", ruta.read_text(encoding="utf-8"))
        filas.append((len(DECISION_JS.findall(codigo)), len(FUNCION_JS.findall(codigo)),
                      len(codigo.splitlines()), ruta.name))
    print(f"{'Componente':28} {'Líneas':>7} {'Funciones':>10} {'Decisiones':>11}")
    for decisiones, funciones, lineas, nombre in sorted(filas, reverse=True)[:args.top]:
        print(f"{nombre:28} {lineas:7} {funciones:10} {decisiones:11}")


# ── Suite CK ──────────────────────────────────────────────────────────────────
def nombres_usados(nodo: ast.AST) -> set:
    """Nombres y atributos referenciados, más textos usados como nombre de clase."""
    usados = set()
    for n in ast.walk(nodo):
        if isinstance(n, ast.Name):
            usados.add(n.id)
        elif isinstance(n, ast.Attribute):
            usados.add(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.isidentifier():
            usados.add(n.value)  # relationship("Category")
    return usados


def llamadas(nodo: ast.AST) -> set:
    nombres = set()
    for n in ast.walk(nodo):
        if isinstance(n, ast.Call):
            f = n.func
            nombres.add(f.id if isinstance(f, ast.Name) else getattr(f, "attr", "?"))
    return nombres


def lcom(miembros: dict) -> int:
    """LCOM de Chidamber y Kemerer: pares sin atributos comunes menos pares con ellos (mínimo 0)."""
    p = q = 0
    for a, b in itertools.combinations(miembros.values(), 2):
        if a & b:
            q += 1
        else:
            p += 1
    return max(p - q, 0)


def lcom4(miembros: dict) -> int:
    """LCOM4 de Hitz y Montazeri: componentes conexas del grafo de métodos.

    Dos métodos se conectan si comparten un atributo o si uno usa al otro.
    1 indica una unidad cohesiva; más de 1, responsabilidades separables.
    """
    nombres = list(miembros)
    grupo = {n: n for n in nombres}

    def raiz(n):
        while grupo[n] != n:
            n = grupo[n]
        return n

    for a, b in itertools.combinations(nombres, 2):
        if miembros[a] & miembros[b] or a in miembros[b] or b in miembros[a]:
            grupo[raiz(a)] = raiz(b)
    return len({raiz(n) for n in nombres})


def cmd_ck(args) -> None:
    raiz = pathlib.Path(args.raiz)
    arboles = dict(modulos(raiz))
    clases = {c.name: (ruta, c) for ruta, arbol in arboles.items() for c in arbol.body if isinstance(c, ast.ClassDef)}
    nombres_modulo = {r.stem for r in arboles}
    padre = {n: [getattr(b, "id", getattr(b, "attr", "")) for b in c.bases] for n, (_, c) in clases.items()}

    def dit(nombre):
        bases = [b for b in padre.get(nombre, []) if b]
        if not bases:
            return 0
        return 1 + max((dit(b) if b in clases else 0) for b in bases)

    print("Clases (atributos = campos de la clase y nombres usados por cada método)")
    print(f"{'Clase':22} {'Módulo':20} {'NOM':>4} {'WMC':>4} {'DIT':>4} {'NOC':>4} {'CBO':>4} {'RFC':>4} {'LCOM':>5} {'LCOM4':>5}")
    for nombre, (ruta, c) in sorted(clases.items(), key=lambda x: (x[1][0].name, x[0])):
        metodos = [m for m in c.body if isinstance(m, FUNCIONES)]
        campos = {t.id for s in c.body if isinstance(s, (ast.Assign, ast.AnnAssign))
                  for t in (s.targets if isinstance(s, ast.Assign) else [s.target]) if isinstance(t, ast.Name)}
        cbo = len((nombres_usados(c) & set(clases)) - {nombre} - set(padre[nombre]))
        rfc = len(metodos) + len(set().union(*(llamadas(m) for m in metodos)) if metodos else set())
        noc = sum(nombre in b for b in padre.values())
        miembros = {m.name: (nombres_usados(m) & campos) or {f"_{m.name}"} for m in metodos}
        print(f"{nombre:22} {ruta.name:20} {len(metodos):4} {sum(complejidad(m) for m in metodos):4} "
              f"{dit(nombre):4} {noc:4} {cbo:4} {rfc:4} {lcom(miembros):5} {lcom4(miembros) if miembros else 0:5}")

    print("\nMódulos como clase (métodos = funciones; atributos = nombres globales del módulo)")
    print(f"{'Módulo':32} {'NOM':>4} {'WMC':>4} {'CBO':>4} {'RFC':>4} {'LCOM':>5} {'LCOM4':>5}")
    for ruta, arbol in arboles.items():
        funciones = [f for f in arbol.body if isinstance(f, FUNCIONES)]
        if not funciones:
            continue
        globales = {t.id for s in arbol.body if isinstance(s, ast.Assign) for t in s.targets if isinstance(t, ast.Name)}
        globales |= {f.name for f in funciones}
        internos = set()
        for s in arbol.body:
            if isinstance(s, ast.ImportFrom) and (s.level or (s.module or "").startswith("app")):
                internos |= {a.name for a in s.names if a.name in nombres_modulo or a.name in clases}
                if s.module and s.module.split(".")[-1] in nombres_modulo:
                    internos.add(s.module.split(".")[-1])
        internos.discard(ruta.stem)
        rfc = len(funciones) + len(set().union(*(llamadas(f) for f in funciones)))
        # Un global que agrupa funciones (p. ej., _RANGES) conecta a quien lo usa con ellas
        alias = {t.id: nombres_usados(s.value) & globales for s in arbol.body if isinstance(s, ast.Assign)
                 for t in s.targets if isinstance(t, ast.Name)}
        miembros = {}
        for f in funciones:
            usados = nombres_usados(f) & globales
            usados |= set().union(*(alias.get(g, set()) for g in usados))
            miembros[f.name] = (usados - {f.name}) or {f"_{f.name}"}
        print(f"{ruta.relative_to(raiz).as_posix():32} {len(funciones):4} "
              f"{sum(complejidad(f) for f in funciones):4} {len(internos):4} {rfc:4} {lcom(miembros):5} {lcom4(miembros):5}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="medicion")
    p = sub.add_parser("complejidad")
    p.add_argument("--raiz", default="backend/app")
    p.add_argument("--umbral", type=int, default=10)
    p.set_defaults(func=cmd_complejidad)
    p = sub.add_parser("tamano")
    p.add_argument("--raiz", default=".")
    p.add_argument("--sin-pruebas", action="store_true", help="excluye el código de pruebas")
    p.set_defaults(func=cmd_tamano)
    p = sub.add_parser("frontend")
    p.add_argument("--raiz", default="frontend/src")
    p.add_argument("--top", type=int, default=8)
    p.set_defaults(func=cmd_frontend)
    p = sub.add_parser("ck")
    p.add_argument("--raiz", default="backend/app")
    p.set_defaults(func=cmd_ck)
    args = parser.parse_args()
    if not args.medicion:  # compatibilidad: sin subcomando mide la complejidad
        args = parser.parse_args(["complejidad"])
    args.func(args)


if __name__ == "__main__":
    main()

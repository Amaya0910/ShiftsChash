"""Genera docs/ShiftCash_Complementos_Entrega_Final.docx con python-docx."""
import os
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

AQUI = os.path.dirname(os.path.abspath(__file__))
DIAG = os.path.join(AQUI, "diagramas")
SALIDA = os.path.join(AQUI, "ShiftCash_Complementos_Entrega_Final.docx")

doc = Document()
st = doc.styles["Normal"]
st.font.name = "Times New Roman"
st.font.size = Pt(11.5)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.15
for n, tam in (("Heading 1", 16), ("Heading 2", 13.5), ("Heading 3", 12)):
    h = doc.styles[n]
    h.font.name = "Times New Roman"
    h.font.size = Pt(tam)
    h.font.color.rgb = RGBColor(0x1F, 0x4E, 0x79)
    h.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
sec = doc.sections[0]
sec.left_margin = sec.right_margin = Cm(2.3)
sec.top_margin = sec.bottom_margin = Cm(2.2)

N_TABLA = [0]
N_FIG = [0]


def p(texto, negrita_ini=None, cursiva=False, tam=None, centro=False):
    par = doc.add_paragraph()
    if negrita_ini:
        r = par.add_run(negrita_ini)
        r.bold = True
    r = par.add_run(texto)
    r.italic = cursiva
    if tam:
        r.font.size = Pt(tam)
    if centro:
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return par


def viñetas(items, estilo="List Bullet"):
    for it in items:
        par = doc.add_paragraph(style=estilo)
        if isinstance(it, tuple):
            par.add_run(it[0]).bold = True
            par.add_run(it[1])
        else:
            par.add_run(it)


def nota(texto):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    c = t.cell(0, 0)
    sombrear(c, "FFF4CC")
    c.paragraphs[0].add_run("Para completar por el equipo: ").bold = True
    c.paragraphs[0].add_run(texto)
    doc.add_paragraph()


def sombrear(celda, color):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color)
    tcPr.append(shd)


def tabla(titulo, encabezado, filas, anchos=None, tam=9):
    N_TABLA[0] += 1
    cap = doc.add_paragraph()
    cap.add_run(f"Tabla C{N_TABLA[0]}").bold = True
    cap.add_run("\n")
    cap.add_run(titulo).italic = True
    cap.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(encabezado))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(encabezado):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(tam)
        sombrear(c, "DCE6F1")
    for fila in filas:
        cells = t.add_row().cells
        for i, v in enumerate(fila):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(tam)
    if anchos:
        for fila in t.rows:
            for i, w in enumerate(anchos):
                fila.cells[i].width = Cm(w)
    doc.add_paragraph()
    return t


def figura(archivo, titulo, ancho=16):
    N_FIG[0] += 1
    cap = doc.add_paragraph()
    cap.add_run(f"Figura C{N_FIG[0]}").bold = True
    cap.add_run("\n")
    cap.add_run(titulo).italic = True
    cap.paragraph_format.keep_with_next = True
    doc.add_picture(os.path.join(DIAG, archivo), width=Cm(ancho))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER


def donde(texto):
    par = doc.add_paragraph()
    r = par.add_run("Ubicación en el documento: " + texto)
    r.italic = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x7A, 0x4E, 0x1F)


# ═════════════════════════════════════════════════════════════════════════════
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("ShiftCash\nComplementos y correcciones para la entrega final")
r.bold = True
r.font.size = Pt(18)
p("Brayan Vásquez e Isabella Amaya · Ingeniería de Software G03 · Universidad Popular del Cesar",
  centro=True, tam=11)
p("Documento de trabajo, noviembre de 2026", centro=True, cursiva=True, tam=10)

doc.add_heading("Cómo usar este documento", level=1)
p("Este documento reúne lo que le falta al informe «Proyecto de aula» (versión del 25 de octubre de 2026) "
  "para cumplir el nivel Sobresaliente de la rúbrica RAP – Momento 2. Cada sección indica en qué parte del "
  "informe va y qué ítem de la rúbrica atiende. Las tablas y figuras se numeran con el prefijo «C» para no "
  "chocar con la numeración del informe; al insertarlas, renumérenlas en orden. Los recuadros amarillos "
  "marcan datos que solo el equipo puede aportar (por ejemplo, los resultados con usuarios reales); no se "
  "llenaron con cifras inventadas.")
tabla("Mapa de las secciones nuevas frente a la rúbrica", ["Sección de este documento", "Dónde va en el informe", "Ítem de la rúbrica (peso)"], [
    ["1. Problema e impacto medido", "Primera Parte, reemplaza 1.1", "1.1 Planteamiento (3 %)"],
    ["2. Causas y efectos", "Primera Parte, nuevo 1.2", "1.2 Causas y efectos (2 %)"],
    ["3. Alcance y valor", "Primera Parte, nuevo apartado tras el objetivo", "2.2 Alcance y valor (2 %)"],
    ["4. Metodología y cronograma", "Primera Parte, reemplaza 1.6", "7.3 Coherencia con el cronograma (4 %)"],
    ["5. Requisitos funcionales verificables", "Primera Parte, reemplaza la Tabla 3", "3.1 RF (4 %)"],
    ["6. Requisitos no funcionales medibles", "Primera Parte, reemplaza la Tabla 4", "3.2 RNF (4 %)"],
    ["7. Casos de uso completos y trazabilidad", "Primera Parte, amplía la sección 3", "3.3 Casos de uso (4 %)"],
    ["8. Diagrama de clases de la implementación", "Primera Parte, nuevo 4.2 (antes de relaciones)", "4.1 Diagrama de clases (5 %)"],
    ["9. Registro y corrección de defectos", "Reemplaza el Apéndice F", "6.2 Integración (6 %), 5.1 Funcionalidad (7 %)"],
    ["10. Pruebas automatizadas con pytest y cobertura", "Segunda Parte, sección 3.6 y nueva 4.5", "6.1 Unitarias (6 %), 6.2 (6 %)"],
    ["11. Aceptación con usuarios finales", "Segunda Parte, sección 6", "6.3 Aceptación (6 %)"],
    ["12. Métricas CK completas", "Tercera Parte, sección 5.2", "6.4 Métricas internas (6 %)"],
    ["13. Presupuesto con recursos", "Cuarta Parte, nuevo apartado antes del análisis comparativo", "7.3 Esfuerzo y costo (4 %)"],
    ["14. Fe de erratas", "Varias secciones", "Coherencia general y 8.3 Dominio"],
    ["15. Guía para la sustentación", "Presentación (plantilla)", "8.1, 8.2 y 8.3 (10 %)"],
], anchos=[5.5, 6, 5])

# ── 1 ────────────────────────────────────────────────────────────────────────
doc.add_heading("1. Identificación del problema e impacto medido", level=1)
donde("Primera Parte, reemplaza el texto de 1.1 «Identificación del problema». Rúbrica 1.1.")
p("Las personas jóvenes y adultas que manejan sus propios ingresos, como estudiantes universitarios, "
  "trabajadores independientes y empleados con salario quincenal o mensual, no llevan un registro sistemático de "
  "su dinero. Hoy, quien intenta controlarlo anota sus gastos en un cuaderno, en notas del celular o en una hoja de "
  "cálculo. Lo hace de forma irregular, sin categorías estables y sin un límite de gasto por rubro, de modo "
  "que solo descubre que gastó de más cuando el dinero ya no alcanza. Los movimientos que se repiten (arriendo, "
  "salario, suscripciones) hay que copiarlos a mano cada período, y las metas de ahorro se plantean como un monto "
  "final sin un plan diario que permita ver el avance. El problema ocurre en el día a día de cada persona, "
  "en su celular o computador, y no depende de una organización.")
p("Queda fuera del proyecto: la conexión con bancos o billeteras digitales (los movimientos se registran "
  "manualmente), la asesoría de inversión, el manejo de deudas y créditos, la facturación y la contabilidad de "
  "empresas, y las finanzas compartidas entre varios usuarios.", negrita_ini="Fuera del alcance. ")
p("El problema tiene magnitud medida en fuentes públicas:", negrita_ini="Impacto medido. ")
viñetas([
    ("Solo el 11,1 % de los colombianos ", "podría cubrir por completo un gasto imprevisto grande con sus propios "
     "recursos (Bloomberg Línea, 2022, con datos de la encuesta de demanda de inclusión financiera de Banca de las "
     "Oportunidades)."),
    ("Más del 39 % de los colombianos ", "siente que le falta dinero para llegar al final del mes (La República, "
     "con datos de la medición de bienestar financiero de Banca de las Oportunidades)."),
])
p("Estas cifras sirven de línea base: ShiftCash busca que el usuario sepa en todo momento cuánto lleva gastado "
  "frente a su presupuesto (alerta al 80 %) y que su meta de ahorro avance cada día.")
nota("verifiquen las dos cifras en la fuente original antes de citarlas y agreguen la referencia completa en APA. "
     "Para la evidencia primaria que pide el nivel Alto, apliquen una encuesta breve a al menos 15 o 20 compañeros "
     "con las preguntas de la Tabla C2 y reporten los porcentajes con la fecha y el número de respuestas.")
tabla("Instrumento de encuesta para medir el problema (evidencia primaria)", ["#", "Pregunta", "Respuestas", "Resultado (n = __)"], [
    ["1", "¿Registras tus gastos al menos una vez por semana?", "Sí / No", "__ % sí"],
    ["2", "¿Dónde los registras?", "Cuaderno / Notas / Excel / App / No registro", "__ % por opción"],
    ["3", "¿Cuántos minutos a la semana dedicas a registrar y revisar tus gastos?", "Número", "Media: __ min"],
    ["4", "En el último mes, ¿gastaste más de lo que planeabas en algún rubro?", "Sí / No", "__ % sí"],
    ["5", "¿Has abandonado una meta de ahorro antes de cumplirla?", "Sí / No", "__ % sí"],
    ["6", "¿Usarías una app que te alerte al llegar al 80 % de tu presupuesto?", "Escala 1–5", "Media: __"],
], anchos=[0.8, 7.5, 4.5, 3.5])

# ── 2 ────────────────────────────────────────────────────────────────────────
doc.add_heading("2. Causas y efectos del problema", level=1)
donde("Primera Parte, nuevo apartado 1.2 (renumerar los siguientes). Rúbrica 1.2.")
figura("arbol_problema.png", "Árbol de problemas de ShiftCash: causas, problema central y efectos", 16)
tabla("Causas del problema y cómo las ataca la solución", ["Causa", "Por qué conduce al problema", "Cómo la ataca ShiftCash"], [
    ["C1. Registro manual lento y con errores", "Registrar a mano cuesta tiempo y se abandona; las sumas se hacen mal.",
     "Formulario guiado con categoría, validación de monto y fecha por defecto (CU01, RF03)."],
    ["C2. Sin límites de gasto por categoría ni alertas", "Sin un tope por rubro no hay forma de saber que se está gastando de más.",
     "Presupuestos por categoría y período con porcentaje ejecutado y alerta al 80 % (CU02, CU09, RF11–RF14)."],
    ["C3. Ahorro sin plan diario", "Una meta grande sin pasos pequeños se percibe inalcanzable.",
     "Plan de cuotas diarias variables y marcado de días con progreso (CU03, CU12, RF15–RF18)."],
    ["C4. Movimientos recurrentes olvidados", "El arriendo o el salario se olvidan y el saldo real no coincide.",
     "Transacciones recurrentes generadas automáticamente cada día a las 00:05 (CU13, RF04–RF05)."],
], anchos=[4.2, 5.5, 6.5])
tabla("Efectos del problema", ["Efecto", "Cómo se deriva del problema"], [
    ["E1. Gastos «hormiga» y sobregiros no detectados", "Sin registro sistemático, los gastos pequeños no se ven hasta que suman."],
    ["E2. Endeudamiento y falta de dinero a fin de mes", "Al gastar sin límite, el ingreso se agota antes del siguiente pago (más del 39 % lo percibe)."],
    ["E3. Metas de ahorro abandonadas", "Sin plan ni avance visible, la meta se pospone."],
    ["E4. Decisiones financieras sin información", "No se sabe en qué rubro se va el dinero ni cómo cambia mes a mes."],
], anchos=[6, 10])

# ── 3 ────────────────────────────────────────────────────────────────────────
doc.add_heading("3. Alcance del sistema y valor de la solución", level=1)
donde("Primera Parte, después de 1.3 «Objetivo general». Rúbrica 2.2.")
tabla("Alcance de ShiftCash", ["Incluye (versión entregada)", "No incluye"], [
    ["Registro, inicio de sesión con correo o Google y gestión del perfil (RF01, RF02, RF19, RF20)",
     "Conexión automática con bancos, Nequi, Daviplata u otras billeteras"],
    ["Transacciones de ingreso y gasto, con recurrencias automáticas (RF03–RF07)", "Gestión de deudas, créditos o tarjetas"],
    ["Categorías predeterminadas y personalizadas (RF10)", "Inversiones, cripto o asesoría financiera"],
    ["Presupuestos por categoría con alerta configurable (RF11–RF14)", "Finanzas compartidas entre varios usuarios o familias"],
    ["Metas de ahorro con plan diario y progreso (RF15–RF18)", "Aplicación móvil nativa (se usa la web responsiva)"],
    ["Resumen y gráficas de los movimientos (RF08, RF09)", "Exportación a Excel o PDF y recuperación de contraseña por correo"],
], anchos=[8.5, 7.5])
tabla("Valor frente a otras formas de resolver el problema", ["Criterio", "Cuaderno o Excel", "Apps genéricas de finanzas", "ShiftCash"], [
    ["Costo", "Gratis", "Gratis con anuncios o suscripción", "Gratis, web, sin instalación"],
    ["Cálculo del gasto frente al presupuesto", "Manual, con fórmulas", "Automático", "Automático, por período diario, semanal, mensual o único"],
    ["Alerta antes de pasarse", "No", "Algunas", "Sí, umbral configurable (80 % por defecto)"],
    ["Plan de ahorro diario", "No", "Rara vez", "Sí: cuotas variables, redondeadas a la moneda y con suma exacta"],
    ["Movimientos recurrentes", "Copiar a mano", "Sí", "Sí, generados a diario sin duplicados"],
    ["Idioma y moneda local", "—", "Muchas en inglés o USD", "Español; COP por defecto (también USD, EUR, MXN)"],
], anchos=[3.8, 3.4, 4, 4.8])
p("Para decir «en cuánto» mejora la solución, comparen el tiempo de la tarea cronometrada PU-06 (registrar un gasto "
  "en ShiftCash) con el tiempo que reporte la pregunta 3 de la encuesta, y el porcentaje de usuarios que "
  "sobrepasaron un presupuesto (pregunta 4) frente a lo que muestra la alerta.")

# ── 4 ────────────────────────────────────────────────────────────────────────
doc.add_heading("4. Metodología de desarrollo y cronograma", level=1)
donde("Primera Parte, reemplaza 1.6 «Metodología identificada». Rúbrica 7.3 y criterio «Realista».")
p("El equipo usó un marco ágil basado en Scrum, adaptado a dos integrantes, con un tablero Kanban para "
  "visualizar el trabajo. Se trabajó en sprints de dos semanas; al inicio de cada sprint se tomaban historias "
  "del backlog (las 15 historias de usuario de la Cuarta Parte, 89 puntos) y al final se revisaba el incremento "
  "funcionando. El tablero tenía las columnas Por hacer, En progreso, En revisión y Hecho, con un límite de dos "
  "tarjetas en progreso por persona. La definición de terminado de cada historia fue: código en la rama "
  "principal, prueba manual del flujo y despliegue en Vercel o Render.")
tabla("Roles del equipo", ["Rol", "Responsable", "Responsabilidades"], [
    ["Product Owner y desarrollo frontend", "[completar]", "Priorizar el backlog, React/Vite, vistas y modales"],
    ["Scrum Master y desarrollo backend", "[completar]", "Seguimiento del tablero, FastAPI, base de datos, despliegue"],
    ["Calidad (compartido)", "Ambos", "Plan de pruebas, ejecución de herramientas, métricas y estimación"],
], anchos=[5, 3.5, 7.5])
figura("cronograma.png", "Cronograma del proyecto ShiftCash por sprints", 16.5)
nota("el cronograma se reconstruyó con el historial de Git (primer commit el 13 de agosto y despliegue el 17 de "
     "octubre de 2026) y las fechas del informe. Ajusten las fechas de cada sprint y los nombres de los roles a lo "
     "que realmente hicieron, y agreguen una captura del tablero Kanban (Trello, GitHub Projects o Notion) para la "
     "diapositiva 5. Las fechas están en docs/diagramas/generar_diagramas.py (lista TAREAS); al cambiarlas, vuelvan "
     "a generar la figura.")
p("Coherencia con la estimación: el desarrollo funcional tomó unas 9 semanas (≈ 2,1 meses) con 2 personas, "
  "cercano a los 2,23 meses y 4,45 PM de los puntos de historia, que fue el modelo propuesto como más viable en "
  "la Cuarta Parte.")

# ── 5 ────────────────────────────────────────────────────────────────────────
doc.add_heading("5. Requisitos funcionales con prioridad y criterio verificable", level=1)
donde("Primera Parte, reemplaza la Tabla 3. Rúbrica 3.1 (prioridad MoSCoW: Alta = Must, Media = Should, Baja = Could).")
RF = [
    ["RF01", "Registrar un usuario con nombre de usuario, correo único y contraseña de al menos 8 caracteres.", "Alta",
     "Con correo repetido responde 400; con contraseña de 7 caracteres responde 422; con datos válidos crea el usuario.", "test_registro_correo_duplicado"],
    ["RF02", "Iniciar sesión con correo y contraseña o con Google OAuth y recibir un JWT.", "Alta",
     "Credenciales válidas devuelven access_token; contraseña errada devuelve 401.", "test_login_contrasena_incorrecta, PA-01"],
    ["RF03", "Registrar un ingreso o gasto con categoría, monto > 0, descripción opcional y fecha (por defecto hoy).", "Alta",
     "Monto 0, negativo o > 9,99×10¹² responde 422; sin fecha guarda la fecha actual.", "PI-01, PI-03, PA-02"],
    ["RF04", "Marcar una transacción como recurrente con frecuencia mensual, semanal, quincenal o anual.", "Media",
     "Sin frecuencia, el formulario muestra «Selecciona la frecuencia de repetición».", "PA-03, PA-04"],
    ["RF05", "Generar a diario las transacciones recurrentes que correspondan, sin duplicarlas.", "Media",
     "Dos ejecuciones el mismo día crean una sola instancia.", "test_pi08_recurrente…, test_toca_hoy (10 casos)"],
    ["RF06", "Editar y eliminar transacciones propias.", "Alta",
     "Un usuario no ve ni modifica transacciones de otro.", "test_aislamiento_entre_usuarios"],
    ["RF07", "Consultar el historial con búsqueda y filtros por tipo, categoría, recurrencia y fechas.", "Media",
     "Al filtrar por «gasto» solo aparecen gastos.", "PA (interfaz)"],
    ["RF08", "Visualizar el resumen: total gastado, ganado, ahorrado y número de transacciones.", "Alta",
     "Tras registrar un gasto de $45.000 el total gastado aumenta en $45.000.", "PA-02"],
    ["RF09", "Visualizar gráficas de torta, barras y áreas.", "Baja", "Cada categoría con gasto aparece en la torta.", "Inspección (Figura 17)"],
    ["RF10", "Listar categorías y crear, editar o eliminar solo las personalizadas.", "Media",
     "Eliminar una predeterminada responde 404; una en uso responde 409.", "test_pi05_d05…, test_no_elimina_…"],
    ["RF11", "Crear un presupuesto por categoría con nombre, monto > 0 y período diario, semanal, mensual o único.", "Alta",
     "Mes 13 responde 422; período único sin fechas responde 422.", "PI-09, test_presupuesto_unico_…"],
    ["RF12", "Calcular el gasto ejecutado y el porcentaje real de cada presupuesto en su rango.", "Alta",
     "Gasto 700.000 sobre 600.000 muestra 116,67 % y estado «superado».", "PI-04, PA-06"],
    ["RF13", "Editar y eliminar presupuestos propios.", "Media", "Otro usuario recibe 404.", "test_presupuesto_ajeno_404"],
    ["RF14", "Alertar cuando el gasto del período supere el umbral configurado (80 % por defecto).", "Media",
     "Con 85 % de ejecución aparece la alerta en Resumen.", "PA (interfaz)"],
    ["RF15", "Crear una meta de ahorro con nombre, monto múltiplo de 1000, fechas e imagen opcional.", "Alta",
     "Monto 1500 muestra el mensaje de múltiplo de 1000; sin fecha final usa 30 días.", "PA-08, PI-10"],
    ["RF16", "Generar el plan de cuotas diarias con suma igual al objetivo y sin cuotas negativas.", "Alta",
     "1000 COP en 15 días: suma 1000 y ninguna cuota < 0.", "test_d01_…, PI-06, PA-07"],
    ["RF17", "Marcar y desmarcar días completados y calcular el progreso.", "Alta",
     "Marcar los días 1 y 3 suma exactamente sus cuotas.", "PI-07, PA-09"],
    ["RF18", "Editar la meta (recalculando el plan) y eliminarla.", "Media", "Al cambiar el objetivo, el nuevo plan suma el nuevo objetivo.", "test_editar_meta_regenera_plan"],
    ["RF19", "Gestionar el perfil: nombre, correo, contraseña, moneda, foto (≤ 3 MB) y eliminación de la cuenta.", "Media",
     "Cambiar la moneda a USD hace que la meta nueva use centavos.", "test_d08_meta_usa_moneda_del_usuario"],
    ["RF20", "Alternar entre tema claro y oscuro y conservar la preferencia.", "Baja", "Al recargar la página se mantiene el tema elegido.", "Inspección"],
]
tabla("Requisitos funcionales con prioridad y criterio de aceptación", ["ID", "Descripción", "Prioridad", "Criterio verificable", "Prueba que lo verifica"],
      RF, anchos=[1.2, 5.2, 1.6, 5, 3.6], tam=8)

# ── 6 ────────────────────────────────────────────────────────────────────────
doc.add_heading("6. Requisitos no funcionales medibles (ISO/IEC 25010)", level=1)
donde("Primera Parte, reemplaza la Tabla 4. Rúbrica 3.2. Se indica entre paréntesis el nombre de la característica "
      "en ISO/IEC 25010:2023 cuando cambió frente a la versión 2011.")
RNF = [
    ["RNF01", "Seguridad / confidencialidad", "% de contraseñas guardadas con hash bcrypt y sal", "100 %", "Inspección de la tabla users y prueba de registro", "100 % (cumple)"],
    ["RNF02", "Seguridad / autenticidad", "% de endpoints de datos que responden 401 sin JWT válido", "100 %", "pytest test_sin_token_responde_401, ZAP", "100 % (cumple)"],
    ["RNF03", "Seguridad / integridad", "Credenciales o usuarios codificados en el código fuente", "0", "Revisión de código y test_d06_*", "0 tras corregir D-06 (cumple)"],
    ["RNF04", "Seguridad / confidencialidad", "Redirección de /dashboard sin sesión a /login", "100 % de intentos", "Selenium PA-01", "Cumple"],
    ["RNF05", "Fiabilidad / tolerancia a fallos", "% de entradas inválidas que responden 4xx (no 500)", "100 %", "pytest PI-03, PI-09, PI-10", "100 % tras corregir D-03 y D-07 (antes 2 casos con 500)"],
    ["RNF06", "Portabilidad (flexibilidad) / adaptabilidad", "Navegadores con renderizado correcto; desborde horizontal en 375 px", "4 de 4 (Chrome, Firefox, Edge, Safari); 0 px", "LambdaTest y emulación móvil", "2 de 4 + móvil sin desborde (parcial)"],
    ["RNF07", "Usabilidad (capacidad de interacción) / operabilidad", "Tiempo medio para registrar un gasto; tasa de éxito", "≤ 30 s; ≥ 90 % con 5 usuarios nuevos", "Tarea cronometrada PU-06", "[Pendiente: sesión con usuarios]"],
    ["RNF08", "Adecuación funcional / corrección", "Diferencia entre la suma del plan y el objetivo; cuotas negativas", "0 y 0", "pytest (8 casos parametrizados)", "0 y 0 (cumple)"],
    ["RNF09", "Mantenibilidad / capacidad de prueba", "Cobertura de líneas del backend", "≥ 70 %", "pytest --cov", "80 % (cumple)"],
    ["RNF10", "Mantenibilidad / modificabilidad", "Complejidad ciclomática por función", "≤ 10", "Script de métricas (Apéndice E)", "3 funciones entre 13 y 14 (no cumple)"],
    ["RNF11", "Eficiencia de desempeño / comportamiento temporal", "Tiempo de respuesta p90 y % de error con 50 usuarios concurrentes", "p90 < 2 s; error < 1 %", "JMeter 5.6.3", "Local: p90 10 ms, 0 % (cumple); Render: [pendiente]"],
    ["RNF12", "Fiabilidad / disponibilidad", "Tiempo de arranque en frío de la API; disponibilidad mensual", "≤ 60 s; ≥ 99 %", "Monitor de disponibilidad (UptimeRobot)", "Más de 7 min (D-09, no cumple)"],
    ["RNF13", "Usabilidad / accesibilidad", "% de campos con etiqueta asociada (label for)", "100 %", "Inspección del DOM", "3 de 3 en contacto tras corregir D-10 (cumple)"],
]
tabla("Requisitos no funcionales medibles", ["ID", "Atributo ISO/IEC 25010", "Métrica", "Valor objetivo", "Cómo se verifica", "Resultado"],
      RNF, anchos=[1.2, 3, 3.6, 2.6, 2.9, 3.2], tam=8)

# ── 7 ────────────────────────────────────────────────────────────────────────
doc.add_heading("7. Modelo de casos de uso completo", level=1)
donde("Primera Parte, sección 3. El diagrama general va antes de la Figura 1 (que queda como detalle de las tres "
      "funcionalidades seleccionadas). Rúbrica 3.3 y diapositiva 8 de la plantilla.")
p("El sistema tiene 14 casos de uso, los mismos que se contaron en la estimación por Puntos de Casos de Uso "
  "(Cuarta Parte, Tabla 50). CU01, CU02 y CU03 conservan la especificación de las Tablas 6 a 8; a continuación se "
  "describen los once restantes.")
figura("cu_general.png", "Diagrama general de casos de uso de ShiftCash", 16.5)

CU = [
    ("CU04 Registrarse", "Usuario", "RF01", "No tiene sesión iniciada.",
     "1. Abre /registro. 2. Ingresa nombre de usuario, correo y contraseña. 3. El sistema valida (correo con formato, contraseña ≥ 8). "
     "4. Envía POST /auth/register. 5. El backend verifica que el correo y el usuario no existan, guarda la contraseña con bcrypt y crea el usuario.",
     "E1: correo o usuario repetido → 400. E2: contraseña corta → 422.", "El usuario existe y puede iniciar sesión."),
    ("CU05 Iniciar sesión", "Usuario", "RF02", "El usuario está registrado.",
     "1. Abre /login. 2. Ingresa correo y contraseña. 3. POST /auth/login. 4. El backend verifica el hash y emite un JWT. "
     "5. El cliente guarda el token y abre /dashboard.",
     "E1: credenciales incorrectas → 401 y mensaje. A1: CU06 extiende este caso.", "El usuario tiene un JWT vigente."),
    ("CU06 Iniciar sesión con Google", "Usuario; Google OAuth", "RF02", "Tiene cuenta de Google.",
     "1. Pulsa «Continuar con Google». 2. Google devuelve un access_token. 3. POST /auth/google. 4. El backend consulta userinfo; "
     "si el correo no existe, crea el usuario con nombre único. 5. Emite el JWT.",
     "E1: token de Google inválido → 401. E2: Google no entrega correo → 400.", "Sesión iniciada; usuario creado si era nuevo."),
    ("CU07 Editar o eliminar transacción", "Usuario", "RF06", "Sesión iniciada; existe la transacción.",
     "1. En Historial abre el detalle. 2. Elige Editar, cambia los datos y guarda (PUT /transactions/{id}) o elige Eliminar y confirma (DELETE). "
     "3. El sistema recarga el resumen y los presupuestos.",
     "E1: transacción ajena o inexistente → 404. E2: monto inválido → 422.", "La transacción queda modificada o eliminada."),
    ("CU08 Consultar historial", "Usuario", "RF07", "Sesión iniciada.",
     "1. Abre Historial. 2. El sistema lista las transacciones agrupadas por fecha (GET /transactions/). 3. El usuario busca o filtra por tipo, "
     "categoría, recurrencia, frecuencia o fechas. 4. El sistema muestra solo las que cumplen.",
     "A1: sin resultados → mensaje de lista vacía.", "Ninguna (consulta)."),
    ("CU09 Ver resumen y alertas", "Usuario", "RF08, RF14", "Sesión iniciada.",
     "1. Abre Resumen. 2. El sistema calcula totales de gasto, ingreso, ahorro y número de transacciones. 3. Compara el gasto del período con "
     "el presupuesto total y el umbral. 4. Muestra la meta activa con su progreso.",
     "A1: gasto ≥ umbral → muestra la alerta de presupuesto.", "Ninguna (consulta)."),
    ("CU10 Ver gráficas", "Usuario", "RF09", "Sesión iniciada.",
     "1. Abre Gráficas. 2. El sistema agrupa los movimientos por categoría y por mes. 3. Dibuja la torta de gastos e ingresos y el comparativo mensual.",
     "A1: sin datos → gráficas vacías con mensaje.", "Ninguna (consulta)."),
    ("CU11 Gestionar categorías", "Usuario", "RF10", "Sesión iniciada.",
     "1. Abre Categorías. 2. El sistema lista predeterminadas y propias. 3. El usuario crea, edita o elimina una propia (POST, PUT, DELETE /categories).",
     "E1: nombre vacío o tipo inválido → 422. E2: predeterminada → 404. E3: categoría con transacciones → 409.", "La categoría queda creada, modificada o eliminada."),
    ("CU12 Marcar día ahorrado", "Usuario", "RF17", "Existe una meta del usuario.",
     "1. Abre la plantilla del reto. 2. Marca o desmarca días. 3. Pulsa Guardar. 4. El cliente llama POST /saving-goals/{id}/toggle-day/{n} por cada cambio. "
     "5. El backend actualiza completed_days y devuelve el progreso.",
     "E1: meta ajena → 404.", "Progreso actualizado (total ahorrado, %, días)."),
    ("CU13 Generar transacciones recurrentes", "Programador de tareas (tiempo)", "RF05", "Existen transacciones recurrentes.",
     "1. A las 00:05 se ejecuta registrar_recurrentes. 2. Recorre las recurrentes. 3. Evalúa _toca_hoy según la frecuencia. "
     "4. Si no existe la instancia del día, la crea.",
     "A1: ya existe la instancia → no la duplica.", "Las transacciones del día quedan registradas."),
    ("CU14 Gestionar perfil y preferencias", "Usuario", "RF19, RF20", "Sesión iniciada.",
     "1. Abre Configuración. 2. Cambia nombre y correo (PUT /users/me), contraseña (PUT /users/me/password), moneda, foto o tema. "
     "3. El sistema guarda y muestra confirmación.",
     "E1: contraseña actual incorrecta → 400. E2: foto > 3 MB o formato no permitido → 400. A1: eliminar cuenta → borra en cascada todos sus datos.",
     "Perfil y preferencias actualizados."),
]
for nombre, actores, rf, pre, flujo, alt, post in CU:
    doc.add_heading(nombre, level=3)
    t = doc.add_table(rows=0, cols=2)
    t.style = "Table Grid"
    for k, v in (("Actores", actores), ("Requisitos", rf), ("Precondiciones", pre), ("Flujo básico", flujo),
                 ("Flujos alternos y excepciones", alt), ("Postcondiciones", post)):
        c = t.add_row().cells
        c[0].text = ""
        c[0].paragraphs[0].add_run(k).bold = True
        sombrear(c[0], "EEF3F8")
        c[1].text = v
        for c_ in c:
            for par in c_.paragraphs:
                for r in par.runs:
                    r.font.size = Pt(9)
        c[0].width = Cm(4)
        c[1].width = Cm(12.5)
    doc.add_paragraph()

doc.add_heading("Matriz de trazabilidad casos de uso ↔ requisitos funcionales", level=2)
MAP = {"CU01": ["RF03", "RF04"], "CU02": ["RF11", "RF12", "RF13"], "CU03": ["RF15", "RF16", "RF18"],
       "CU04": ["RF01"], "CU05": ["RF02"], "CU06": ["RF02"], "CU07": ["RF06"], "CU08": ["RF07"],
       "CU09": ["RF08", "RF14"], "CU10": ["RF09"], "CU11": ["RF10"], "CU12": ["RF17"], "CU13": ["RF05"],
       "CU14": ["RF19", "RF20"]}
rfs = [f"RF{i:02d}" for i in range(1, 21)]
filas = [[cu] + ["X" if rf in MAP[cu] else "" for rf in rfs] for cu in MAP]
filas.append(["Total"] + [str(sum(rf in v for v in MAP.values())) for rf in rfs])
t = tabla("Matriz de trazabilidad (cada RF queda cubierto por al menos un caso de uso)", ["CU"] + [r[2:] for r in rfs], filas, tam=7.5)
p("Los 20 requisitos funcionales quedan cubiertos (ninguna columna en 0). En el encabezado, «01» corresponde a RF01, y así sucesivamente.",
  cursiva=True, tam=9.5)

# ── 8 ────────────────────────────────────────────────────────────────────────
doc.add_heading("8. Diagrama de clases de la implementación", level=1)
donde("Primera Parte, sección 4. Insertar como 4.2 «Diagrama de clases de la implementación» después del modelo "
      "conceptual (Figura 2). Rúbrica 4.1, nivel «Detallado e igual al código».")
p("La Figura 2 del informe es un modelo conceptual del dominio. Para cumplir el criterio «igual al código», la "
  "Figura C4 muestra las clases tal como existen en el backend: las entidades SQLAlchemy de app/models.py, los "
  "esquemas Pydantic de app/schemas.py y los módulos de servicio (routers de FastAPI, auth y scheduler), con sus "
  "atributos, tipos, métodos y relaciones. Todos los nombres coinciden con el código fuente.")
doc.add_section(WD_ORIENT.LANDSCAPE)
s2 = doc.sections[-1]
s2.orientation = WD_ORIENT.LANDSCAPE
s2.page_width, s2.page_height = s2.page_height, s2.page_width
figura("clases_implementacion.png", "Diagrama de clases de la implementación de ShiftCash (backend)", 22)
doc.add_section()
s3 = doc.sections[-1]
s3.orientation = WD_ORIENT.PORTRAIT
s3.page_width, s3.page_height = s3.page_height, s3.page_width
tabla("Correspondencia entre el modelo conceptual y el código", ["Clase conceptual (Figura 2)", "Implementación en el código"], [
    ["Usuario", "models.User (+ esquemas UserCreate, UserOut, UserUpdate)"],
    ["Transacción / TransacciónRecurrente", "models.Transaction con is_recurring y frequency; scheduler._toca_hoy"],
    ["Categoría, CategoríaPredeterminada, CategoríaPersonalizada", "models.Category con la bandera is_default (0 o 1)"],
    ["Presupuesto y PeríodoPresupuesto", "models.Budget (period_type, month, year, start_date, end_date, is_permanent); routes.budgets.get_date_range"],
    ["MetaAhorro y CuotaDiaria", "models.SavingGoal con daily_amounts (JSON) y completed_days (JSON)"],
    ["ProgresoMeta", "Diccionario que devuelve routes.savings.calculate_progress"],
    ["ConfiguraciónMoneda", "routes.savings.CURRENCY_CONFIG y User.currency"],
    ["ResumenFinanciero", "Hook useFinanzas.js en el frontend (calcularResumen)"],
    ["ProgramadorRecurrencias", "scheduler.BackgroundScheduler + registrar_recurrentes"],
], anchos=[6, 10])

# ── 9 ────────────────────────────────────────────────────────────────────────
doc.add_heading("9. Registro de defectos con su corrección", level=1)
donde("Reemplaza la Tabla F1 del Apéndice F. Rúbrica 6.2 (nivel Sobresaliente: «registra los defectos encontrados y su corrección»).")
p("Los defectos se corrigieron en la rama fix/defectos del repositorio. Cada corrección tiene una prueba "
  "automatizada de regresión que falla con el código original (commit 0efe28b) y pasa con el código corregido.")
DEF = [
    ["D-01", "Alta", "Cuota diaria negativa (1 000 COP en 15 días: día 15 = −400).",
     "savings.py: en la rama de objetivo insuficiente se asigna la unidad mínima a los primeros ⌊objetivo/unidad⌋ días con redondeo hacia abajo; el último día recibe el residuo (≥ 0).",
     "test_d01_caso_reportado…, test_plan_suma_objetivo… [15-1000], PI-06", "Corregido"],
    ["D-02", "Media", "No se valida el monto máximo de Numeric(15,2).",
     "schemas.py: _validar_monto con MAX_AMOUNT = 9 999 999 999 999,99 en transacciones, presupuestos y metas.",
     "test_transaccion_monto_invalido[10¹³], PI-03", "Corregido"],
    ["D-03", "Media", "month fuera de 1–12 producía error 500.",
     "schemas.py: validadores de mes (1–12) y año (2000–2100); período único exige fechas con inicio ≤ fin.",
     "test_presupuesto_mes_invalido, PI-09 (ahora 422)", "Corregido"],
    ["D-04", "Media", "El porcentaje se limitaba a 100 y la tarjeta nunca mostraba «superado».",
     "budgets.py: se devuelve el porcentaje real; el frontend ya limita solo el ancho de la barra.",
     "test_pi04_d04_porcentaje_supera_100, PA-06", "Corregido"],
    ["D-05", "Media", "category_id NOT NULL con ON DELETE SET NULL: referencia huérfana.",
     "categories.py: no se elimina una categoría con transacciones (409 con mensaje); models.py: ondelete=\"RESTRICT\".",
     "test_pi05_d05_no_elimina_categoria…, PI-05", "Corregido (en la BD existente la FK solo cambia con una migración)"],
    ["D-06", "Crítica", "Credenciales admin@test.com/123 y usuario 999 codificados.",
     "users.py y auth.py: se eliminó el usuario predeterminado y el endpoint comentado.",
     "test_d06_credenciales…, test_d06_token_de_usuario_999…", "Corregido"],
    ["D-07", "Media", "Meta sin end_date producía error 500 al responder.",
     "savings.py: si no llega fecha final se guarda inicio + 30 días; se valida inicio ≤ fin.",
     "test_pi10_d07_meta_sin_fecha_final", "Corregido"],
    ["D-08", "Baja", "La meta siempre usaba COP e ignoraba la moneda del usuario.",
     "savings.py: se usa current_user.currency al crear y al recalcular el plan.",
     "test_d08_meta_usa_moneda_del_usuario", "Corregido"],
    ["D-09", "Alta", "La API en Render tardó más de 7 min en responder (arranque en frío del plan gratuito).",
     "Mitigación propuesta: monitor que haga GET / cada 10 min (UptimeRobot o cron-job.org) o plan de pago; la página de inicio ya envía un ping.",
     "Medir arranque en frío antes y después (RNF12)", "Pendiente de aplicar"],
    ["D-10", "Baja", "Formulario de contacto sin label asociado ni manejador de envío.",
     "Home.jsx: htmlFor e id en los 3 campos, name, onSubmit que abre el correo y mensaje de estado.",
     "Inspección del DOM (3 de 3 etiquetas); ESLint sin errores", "Corregido (falta definir CORREO_CONTACTO)"],
    ["D-11", "Baja", "Código muerto: cliente de Supabase y mockData.js sin uso (PM-05).",
     "Se eliminaron frontend/src/lib/supabaseClient.js y frontend/src/data/mockData.js.",
     "npm run build y npm run lint sin errores", "Corregido"],
]
tabla("Registro de defectos, corrección y verificación", ["ID", "Sev.", "Descripción", "Corrección aplicada", "Prueba de regresión", "Estado"],
      DEF, anchos=[1.4, 1.3, 3.4, 5, 3.2, 2.2], tam=7.8)

# ── 10 ───────────────────────────────────────────────────────────────────────
doc.add_heading("10. Pruebas automatizadas con pytest y cobertura", level=1)
donde("Segunda Parte: complementa 3.6 «Ejecución y evaluación de las pruebas» y agrega 4.5 «Pruebas de integración "
      "automatizadas». También actualiza PM-02 (Tabla 31) y la cobertura de SonarQube. Rúbrica 6.1 y 6.2.")
p("Las pruebas quedaron en el repositorio, en backend/tests, y se ejecutan con pytest y pytest-cov. Usan una "
  "base de datos SQLite en memoria con las claves foráneas activadas (PRAGMA foreign_keys=ON), para que se comporte "
  "como PostgreSQL en las restricciones, y el TestClient de FastAPI para recorrer cada hilo completo: petición HTTP "
  "con JWT → router → validación Pydantic → SQLAlchemy → base de datos.")
tabla("Suites de prueba automatizadas", ["Archivo", "Nivel y técnica", "Casos", "Qué cubre"], [
    ["tests/test_unitarias.py", "Unitario: caja negra (clases de equivalencia, valores límite) y caja blanca (caminos de generate_daily_amounts, get_date_range, _toca_hoy)", "49",
     "Plan de ahorro, rangos de presupuesto, recurrencias, validaciones de esquemas"],
    ["tests/test_integracion.py", "Integración ascendente basada en hilos (API + ORM + BD)", "23",
     "Autenticación y seguridad, F1, F2, F3, categorías, aislamiento entre usuarios"],
    ["Total", "", "72", ""],
], anchos=[4, 6.5, 1.3, 4.7])
tabla("Resultado de la ejecución (antes y después de corregir)", ["Ejecución", "Aprobadas", "Fallidas", "Cobertura de líneas"], [
    ["Código original (commit 0efe28b)", "53", "19 (todas explicadas por D-01 a D-08)", "—"],
    ["Código corregido (rama fix/defectos)", "72", "0", "80 % (884 sentencias, 178 sin cubrir)"],
], anchos=[5.5, 2.5, 5, 4])
cob = [
    ["app/models.py", "67", "100 %"], ["app/scheduler.py", "33", "97 %"], ["app/main.py", "22", "95 %"],
    ["app/schemas.py", "253", "93 %"], ["app/auth.py", "36", "92 %"], ["app/routes/savings.py", "149", "83 %"],
    ["app/routes/categories.py", "37", "73 %"], ["app/routes/budgets.py", "93", "71 %"], ["app/database.py", "17", "71 %"],
    ["app/routes/transactions.py", "50", "62 %"], ["app/routes/users.py", "50", "52 %"], ["app/routes/profile.py", "77", "42 %"],
    ["Total", "884", "80 %"],
]
tabla("Cobertura por módulo (pytest-cov)", ["Módulo", "Sentencias", "Cobertura"], cob, anchos=[7, 3, 3])
p("Evaluación. La cobertura supera el objetivo de 70 % (RNF09). Los módulos de lógica crítica (modelos, esquemas, "
  "planificador, metas) están por encima del 80 %. Los menos cubiertos son el perfil (subida de foto) y Google OAuth, "
  "que dependen de servicios externos y quedaron fuera del alcance del plan de pruebas. Comandos para reproducir:")
for cmd in ("cd backend", "python -m venv venv && venv\\Scripts\\activate", "pip install -r requirements.txt pytest pytest-cov httpx",
            "pytest --cov=app --cov-report=term --cov-report=html"):
    par = doc.add_paragraph(cmd)
    par.runs[0].font.name = "Consolas"
    par.runs[0].font.size = Pt(9.5)
    par.paragraph_format.left_indent = Cm(1)
    par.paragraph_format.space_after = Pt(0)
doc.add_paragraph()
nota("tomen captura de la salida de pytest en la terminal y del reporte HTML (docs/cobertura_html/index.html) como "
     "evidencia «con herramienta». Si vuelven a analizar con SonarQube, importen el reporte XML (pytest --cov-report=xml) "
     "para que la cobertura deje de aparecer en 0,0 %.")

# ── 11 ───────────────────────────────────────────────────────────────────────
doc.add_heading("11. Pruebas de aceptación con usuarios finales", level=1)
donde("Segunda Parte, sección 6: agregar 6.3 «Ejecución con usuarios finales». Rúbrica 6.3 (hoy queda en «Parciales» "
      "porque las ejecutó el equipo). También completa PU-06 y RNF07.")
p("Protocolo. Se convocan al menos cinco usuarios finales que no participaron en el desarrollo (estudiantes o "
  "trabajadores que manejan sus propios gastos). Cada uno usa la aplicación desplegada en su propio dispositivo, después de "
  "corregir los defectos y desplegar la rama corregida. Un integrante del equipo lee cada escenario sin ayudar, "
  "cronometra la tarea PA-02 (registrar un gasto, que es PU-06) y anota si el usuario la aceptó y qué observó.")
tabla("Resultados por usuario y escenario (llenar en la sesión)", ["Escenario (RF)", "U1", "U2", "U3", "U4", "U5", "% aceptación"], [
    ["PA-01 Ruta privada sin sesión (RNF04)", "", "", "", "", "", ""],
    ["PA-02 Registrar un gasto (RF03, RF08) – tiempo en s", "", "", "", "", "", ""],
    ["PA-03 Gasto recurrente desde la interfaz (RF04)", "", "", "", "", "", ""],
    ["PA-05 Crear presupuesto desde la interfaz (RF11)", "", "", "", "", "", ""],
    ["PA-06 Presupuesto superado se marca (RF12)", "", "", "", "", "", ""],
    ["PA-07 Meta pequeña sin cuotas negativas (RF16)", "", "", "", "", "", ""],
    ["PA-08 Validación de múltiplo de 1000 (RF15)", "", "", "", "", "", ""],
    ["PA-09 Marcar días y ver progreso (RF17)", "", "", "", "", "", ""],
], anchos=[6.5, 1.3, 1.3, 1.3, 1.3, 1.3, 2.5], tam=8.5)
p("Cálculos a reportar:", negrita_ini="")
viñetas([
    "Porcentaje de requisitos aceptados = requisitos con todos sus escenarios aceptados / requisitos evaluados × 100.",
    "Tiempo medio de PU-06 = suma de los tiempos / 5 (objetivo ≤ 30 s), con tasa de éxito ≥ 90 % (RNF07).",
    "Observaciones del usuario agrupadas por tema y la acción que tomó el equipo con cada una (corregida, aceptada como mejora futura o descartada con razón).",
])
doc.add_heading("Acta de aceptación", level=3)
p("En Valledupar, el día ____ de __________ de 2026, los usuarios abajo firmantes ejecutaron los escenarios de "
  "aceptación del sistema ShiftCash en la dirección https://shifts-chash-version-amaya.vercel.app/ y declaran que el "
  "sistema [ ] se acepta / [ ] se acepta con observaciones / [ ] no se acepta, con un ____ % de requisitos aceptados.")
p("Observaciones: _____________________________________________________________________________")
tabla("Firmas", ["Nombre del usuario", "Ocupación", "Firma"], [["", "", ""] for _ in range(5)] + [["Equipo: Brayan Vásquez", "Desarrollador", ""], ["Equipo: Isabella Amaya", "Desarrolladora", ""]],
      anchos=[6, 4, 6])
nota("verifiquen la ciudad del acta. Adjunten el acta firmada escaneada y fotos o capturas de la sesión como anexo.")

# ── 12 ───────────────────────────────────────────────────────────────────────
doc.add_heading("12. Métricas orientadas a clases completas (Chidamber y Kemerer)", level=1)
donde("Tercera Parte, sección 5.2. Complementa WMC, DIT y CBO con NOC, RFC y LCOM numéricos (hoy la cohesión aparece "
      "como «Alta/Media»). Rúbrica 6.4.")
p("Se calcularon con un script sobre el árbol sintáctico de Python (ast) para las 27 clases del backend corregido. "
  "NOC = subclases directas dentro del proyecto. RFC = métodos propios + llamadas distintas que hacen esos métodos. "
  "LCOM (CK, 1994) = pares de métodos que no comparten atributos menos pares que sí comparten (mínimo 0); en los "
  "validadores de Pydantic se toma como atributo el campo que valida cada método.")
CK = [
    ["User, Category, Budget, Transaction, SavingGoal (models.py)", "9–14", "0", "0", "0", "0"],
    ["BudgetBase", "9", "4", "2 (BudgetCreate, BudgetOut)", "9", "6"],
    ["BudgetUpdate", "9", "4", "0", "9", "6"],
    ["SavingGoalCreate", "5", "4", "0", "10", "4"],
    ["SavingGoalUpdate", "4", "2", "0", "6", "1"],
    ["TransactionCreate", "7", "2", "0", "5", "1"],
    ["CategoryCreate", "3", "2", "0", "5", "1"],
    ["UserCreate, PasswordUpdate", "2–3", "1", "0", "4", "0"],
    ["BudgetCreate", "0 (hereda 9)", "1", "0", "3", "0"],
    ["Demás DTO (13 clases sin métodos)", "1–11", "0", "0", "0", "0"],
]
tabla("Métricas CK por clase del backend", ["Clase", "Atributos", "Métodos", "NOC", "RFC", "LCOM"], CK, anchos=[6.2, 2, 1.6, 3, 1.4, 1.4], tam=8.5)
tabla("Comparación con valores de referencia", ["Métrica", "Máximo obtenido", "Referencia", "Interpretación"], [
    ["NOC", "2 (BudgetBase)", "≤ 5 (Rosenberg, 1998)", "Jerarquías poco anchas; el esfuerzo de prueba por herencia es bajo."],
    ["RFC", "10 (SavingGoalCreate)", "≤ 50 (Rosenberg, 1998)", "Las clases responden a pocos mensajes; son fáciles de probar."],
    ["LCOM", "6 (BudgetBase, BudgetUpdate)", "0 = cohesión total; valores altos sugieren dividir la clase", "Es esperable en un DTO: cada validador revisa un campo distinto. No justifica dividir la clase, porque los campos describen el mismo concepto (presupuesto)."],
], anchos=[1.6, 3.4, 4.2, 7.3])
p("Hallazgo. La lógica de negocio no está en clases, sino en funciones de los routers (get_date_range, "
  "calculate_spent, generate_daily_amounts), por eso sus métricas CK son bajas, mientras que su complejidad "
  "ciclomática es la más alta (13 y 14 en update_saving_goal, get_date_range y update_budget). Como mejora se propone "
  "extraer una capa de servicios con clases BudgetService y SavingGoalService. Eso bajaría la complejidad por "
  "función a 10 o menos (RNF10) y quitaría la construcción repetida de BudgetOut y SavingGoalOut (duplicación "
  "detectada en PM-04).")

# ── 13 ───────────────────────────────────────────────────────────────────────
doc.add_heading("13. Presupuesto del proyecto con recursos", level=1)
donde("Cuarta Parte, antes de «6. Análisis comparativo». Rúbrica 7.3 («factores, tarifas y supuestos»).")
p("El costo de personal que usan los modelos (COP 4 000 000 por persona-mes) se complementa con los demás recursos "
  "del proyecto. La tabla usa el esfuerzo y el tiempo de los Puntos de Función (8,00 PM en 5,51 meses), la "
  "referencia elegida para presupuestar una versión de producción.")
tabla("Presupuesto con recursos (escenario de referencia: Puntos de Función)", ["Rubro", "Cantidad", "Valor unitario (COP)", "Total (COP)", "Justificación / fuente"], [
    ["Personal de desarrollo", "8,00 PM", "4 000 000 / PM", "32 000 000", "[Justificar: salario de desarrollador junior + prestaciones; citar fuente salarial]"],
    ["Equipos de cómputo (depreciación)", "2 equipos × 5,51 meses", "[valor del equipo] / 36 meses", "[calcular]", "Depreciación lineal a 3 años"],
    ["Internet", "2 conexiones × 5,51 meses", "[tarifa mensual]", "[calcular]", "Plan residencial de cada integrante"],
    ["Hosting frontend (Vercel Hobby)", "5,51 meses", "0", "0", "Plan gratuito usado en el proyecto"],
    ["Hosting API (Render)", "5,51 meses", "0 (gratuito) o [plan pago]", "[calcular]", "El plan gratuito causa D-09; el pago lo evita"],
    ["Base de datos PostgreSQL", "5,51 meses", "[según proveedor]", "[calcular]", "[Indicar proveedor usado]"],
    ["Dominio propio (opcional)", "1 año", "[tarifa .com o .co]", "[calcular]", "Opcional; hoy se usa el subdominio de Vercel"],
    ["Licencias y herramientas", "—", "0", "0", "VS Code, GitHub, JMeter, ZAP, SonarQube Community, Selenium y pytest son gratuitos"],
    ["Imprevistos", "10 % del subtotal", "—", "[calcular]", "Reserva de contingencia habitual"],
    ["Total", "", "", "[sumar]", ""],
], anchos=[3.4, 2.6, 3, 2.4, 5.1], tam=8.5)
nota("reemplacen los corchetes con precios reales consultados (y la fecha de consulta). Con los valores que usen, el "
     "total sigue siendo coherente con el tamaño (160 PF) porque el componente dominante es el personal.")

# ── 14 ───────────────────────────────────────────────────────────────────────
doc.add_heading("14. Fe de erratas: contradicciones y textos pendientes", level=1)
p("Corrijan estos puntos para que el documento sea coherente consigo mismo. Varios afectan el ítem 8.3: si el "
  "evaluador encuentra una contradicción, la va a preguntar en la sustentación.")
ERR = [
    ["Conclusiones generales, párrafo «Pruebas»", "«Quedan pendientes las evidencias con las herramientas ZAP, JMeter, LambdaTest y la ejecución automatizada en Cypress y Selenium…»",
     "«Las evidencias de ZAP (Figuras 30–32), JMeter (Figuras 33–35), LambdaTest (Figuras 37–38), Selenium (Figuras 44–46) y la suite pytest (72 pruebas, 80 % de cobertura) se presentan en la Segunda Parte.»"],
    ["Tabla 34", "«SonarQube: Información pendiente de completar»", "«SonarQube Community 26.7 (Figura 47)»"],
    ["5.2 Pruebas de rendimiento (diseño) y Apéndice D", "Diseño: 60 s de rampa, incluye POST y se ejecuta contra Render; lo ejecutado fue 30 s, solo GET y en local",
     "Igualar el diseño a lo ejecutado (30 s, GET, local) y declarar como limitación la prueba contra Render, o repetir la corrida con el plan del diseño y agregar el POST al Apéndice D."],
    ["Apéndice C, línea 25", "«selector a confirmar en la ejecución»", "Reemplazar por el selector real usado al ejecutar (por ejemplo, By.NAME, \"category_id\")."],
    ["1.6 Metodología", "«El repositorio no documenta explícitamente la metodología… Información pendiente de completar»", "Reemplazar por la sección 4 de este documento."],
    ["Tabla 4, RNF11", "«Información pendiente de completar»", "Reemplazar la tabla por la Tabla C9 de RNF medibles (sección 6)."],
    ["1.2 Descripción detallada", "«el proveedor concreto de la base de datos es Información pendiente de completar»", "[Indicar el proveedor real: Render PostgreSQL, Supabase, Neon u otro]"],
    ["Tabla 12 (ambiente)", "Versiones de LambdaTest y otras herramientas pendientes", "Indicar las versiones usadas: Cypress, Selenium 4.x, ZAP 2.16.1, JMeter 5.6.3, pytest 8.x."],
    ["PI-08, PF-05, PI-05 en PostgreSQL", "Pendientes", "PI-08 y PF-05: ejecutados por test_pi08_recurrente_genera_instancia_sin_duplicar. PI-05: ejecutado con FK activas (409)."],
    ["Tabla 31, PM-02", "«No existen [pruebas automatizadas]» (fallido)", "«72 pruebas en backend/tests, 80 % de cobertura» (aprobado)."],
    ["Tabla 31, PM-05", "Código muerto: Supabase, login comentado, mockData.js", "Eliminado (D-11 y D-06)."],
    ["3.1 y Tabla 26 (PS-02)", "«existe un usuario temporal codificado»", "Indicar que se detectó (D-06) y se corrigió."],
    ["Cuarta Parte, análisis", "«no hay pruebas automatizadas ni documentación técnica»", "«las pruebas automatizadas se agregaron al final del proyecto»."],
    ["Conclusiones de pruebas y de métricas", "Resultados antes de la corrección", "Agregar un párrafo de resultados después de corregir (sección 10)."],
    ["Tono en todo el documento", "«El repositorio analizado…», «el repositorio no documenta…», «la evidencia apunta a…»",
     "Redactar como autores: «Nuestro repositorio…», «Desarrollamos ShiftCash con…», «Decidimos…»."],
    ["Portabilidad (Tabla 29)", "Safari, Edge y móviles pendientes", "Probar Edge en su equipo y Safari/iOS con el celular de un compañero; documentar con capturas."],
]
tabla("Correcciones de coherencia", ["Ubicación", "Texto actual", "Texto o acción propuesta"], ERR, anchos=[3.5, 6, 7], tam=8.5)

# ── 15 ───────────────────────────────────────────────────────────────────────
doc.add_heading("15. Guía para la sustentación (plantilla de 22 diapositivas)", level=1)
tabla("Contenido sugerido por diapositiva", ["Diap.", "Tema", "Qué mostrar de este documento o del informe"], [
    ["2–3", "Proyecto e introducción", "Nombre, integrantes, lema «Impulsa tus ahorros»"],
    ["4", "Problema", "Párrafo de la sección 1, las dos cifras de impacto y el árbol de problemas (Figura C1)"],
    ["5", "Descripción del sistema", "Captura del tablero Kanban, cronograma (Figura C2) y módulos"],
    ["6–7", "Requisitos", "5 RF de prioridad alta y 5 RNF medibles con su resultado"],
    ["8–9", "Casos de uso", "Diagrama general (Figura C3) y la descripción de CU01"],
    ["10", "Diseño", "Clases de la implementación (Figura C4), un diagrama de secuencia y el de componentes"],
    ["11", "Pantallazos", "Resumen, presupuesto superado al 116 % y plan de ahorro sin cuotas negativas"],
    ["13–16", "Pruebas", "Plan; unitarias e integración: 72 pruebas, antes 53/72 y después 72/72; aceptación con usuarios y % aceptado"],
    ["18–19", "Métricas", "LOC, McCabe y CK; SonarQube, JMeter y ZAP con su análisis"],
    ["20", "Estimación", "Tabla comparativa de los 5 modelos y el presupuesto con recursos"],
    ["21", "Demo", "Flujo continuo: login → gasto → presupuesto superado → meta → marcar día (≤ 3 min)"],
    ["22", "Conclusiones", "Una conclusión de pruebas, una de métricas y una de estimación"],
], anchos=[1.5, 3.5, 11.5])
p("Para que la demo salga fluida (ítem 8.2): despierten la API de Render 15 minutos antes de presentar (abran "
  "https://shiftschash-api.onrender.com/ hasta que responda) o configuren el monitor de D-09. Lleven una "
  "grabación de respaldo y un usuario de prueba con datos ya cargados.")
doc.add_heading("Decisiones que deben poder defender (ítem 8.3)", level=3)
viñetas([
    ("¿Por qué FastAPI y React? ", "Validación declarativa con Pydantic, documentación OpenAPI automática y un frontend SPA desacoplado que se despliega gratis en Vercel."),
    ("¿Por qué Decimal y no float en el plan de ahorro? ", "Para evitar errores de redondeo en dinero; cada cuota es múltiplo exacto de la unidad de la moneda (100 COP)."),
    ("¿Por qué impedir borrar una categoría en uso en vez de dejarla «Sin categoría»? ", "Porque category_id es obligatorio: dejar referencias huérfanas rompe la integridad (D-05). Es mejor reasignar primero."),
    ("¿Por qué el porcentaje real y no limitado a 100? ", "El usuario necesita saber cuánto se pasó; el límite se aplica solo al ancho de la barra en la interfaz."),
    ("¿Por qué SQLite en las pruebas? ", "Aísla las pruebas de la base de producción; con PRAGMA foreign_keys=ON se comporta como PostgreSQL en las restricciones probadas."),
    ("¿Por qué los puntos de historia como estimación más viable? ", "Coinciden con el calendario real (2,23 frente a 2,1 meses), mientras que COCOMO II supone un proceso industrial que el equipo no tiene."),
])

doc.add_heading("Referencias nuevas para agregar", level=1)
for ref in [
    "Bloomberg Línea. (2022, 19 de enero). Solo 11,1 % de colombianos podría hacer frente total a un gasto imprevisto grande. https://www.bloomberglinea.com/2022/01/19/solo-111-de-colombianos-podria-hacer-frente-total-a-un-gasto-imprevisto-grande/",
    "La República. (s. f.). Más de 39 % de los colombianos siente que le falta dinero para llegar al final del mes. https://www.larepublica.co/finanzas/mas-de-39-de-los-colombianos-siente-que-le-falta-dinero-para-llegar-al-final-del-mes-3425985 [completar la fecha al verificar]",
    "Krekel, H., & pytest-dev team. (2025). pytest documentation. https://docs.pytest.org/",
    "Rosenberg, L. H. (1998). Applying and interpreting object oriented metrics. Software Technology Conference, NASA SATC.",
    "International Organization for Standardization. (2023). ISO/IEC 25010:2023. Systems and software engineering – SQuaRE – Product quality model. ISO.",
]:
    par = doc.add_paragraph(ref)
    par.paragraph_format.left_indent = Cm(1.25)
    par.paragraph_format.first_line_indent = Cm(-1.25)

doc.save(SALIDA)
print("Generado:", SALIDA)

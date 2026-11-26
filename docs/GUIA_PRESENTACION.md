# Guía para la entrega y las presentaciones de ShiftCash

- **27 de noviembre:** entrega del documento y presentación ante la docente, con las herramientas y las métricas en vivo.
- **2 de diciembre:** presentación ante jurados: resultados y programa en funcionamiento.

El documento para entregar es `docs/latex/main.pdf`.

---

## 1. Antes del 27 (en este orden)

| # | Qué hacer | Cómo | Para qué |
|---|---|---|---|
| 1 | ✅ Integrar la rama a `main` | Abrir <https://github.com/Amaya0910/ShiftsChash/compare/main...fix/defectos>, **Create pull request** y luego **Merge pull request** | Vercel y Render despliegan las correcciones; se activa el ping de la API |
| 2 | ✅ Revisar Render | En <https://dashboard.render.com>, abrir el servicio `shiftschash-api`. Si dice *Suspended*, reanudarlo; si no se desplegó solo, **Manual Deploy > Deploy latest commit** | Que la API desplegada responda |
| 3 | ✅ Aplicar la migración en Supabase | Supabase > SQL Editor > pegar `backend/migraciones/001_transacciones_categoria_restrict.sql` > Run | Que la base de producción impida borrar categorías con transacciones (D-05) |
| 4 | ✅ Probar el ping | GitHub > Actions > **Mantener API despierta** > **Run workflow** | Comprobar que la API y la base responden (`/salud`) |
| 5 | Verificar todo | `powershell -ExecutionPolicy Bypass -File scripts\demo\00_verificar.ps1` | Todo debe salir en `[OK]` |
| 6 | Hacer la prueba de aceptación y PU-06 | Sección 2 | Completar los resultados del documento |
| 7 | Pasar los resultados al documento | Editar solo `docs/latex/resultados.tex` y recompilar (sección 2.4) | Quitar los últimos 18 PENDIENTE |

> Si Render no vuelve, la demostración se hace en local (`01_levantar_app.ps1`) y en el documento queda que la API desplegada no respondió.

---

## 2. Prueba de aceptación (la hacen ustedes)

### 2.1 Preparación
1. Imprimir el **acta** (Apéndice G del PDF) o llenarla en digital.
2. Abrir la app **desplegada**: <https://shifts-chash-version-amaya.vercel.app>.
3. Quien hace de usuario final crea **su propia cuenta** (es el caso PA-10).
4. El otro integrante lee cada caso en voz alta, **no ayuda** y anota en el acta: A (aceptado) o R (rechazado), más lo que diga el usuario.

### 2.2 Casos y qué verificar

| Caso | Qué hacer | Se acepta si… |
|---|---|---|
| PA-01 | Abrir `/dashboard` sin iniciar sesión | Lo manda a `/login` |
| PA-10 | Registrarse; cerrar sesión; volver a entrar | Entra al dashboard con su nombre |
| PA-02 | «+ Transacción»: gasto de 45 000 en Alimentación, «Almuerzo» | Aparece en el historial y el total gastado sube 45 000 |
| PA-03 | Ingreso de 2 500 000, Salario, recurrente mensual | En el historial tiene el ícono de recurrente 🔁 |
| PA-04 | Activar «recurrente» sin elegir frecuencia y guardar | No deja guardar y pide la frecuencia |
| PA-11 | Abrir «Almuerzo», cambiar a 40 000; luego eliminarla | Se ve el cambio; al borrarla desaparece y el total baja |
| PA-12 | Buscar «Almuerzo»; filtrar por tipo y por fechas | Solo aparecen las que cumplen el filtro |
| PA-16 | Crear la categoría «Mascotas», registrar un gasto en ella e intentar borrarla | No deja borrarla y lo explica |
| PA-05 | Presupuesto «Comida del mes», Alimentación, 600 000, mensual | Aparece la tarjeta con el gasto ya registrado |
| PA-06 | Registrar gastos de Alimentación hasta pasar 600 000 | La tarjeta muestra más de 100 % en rojo |
| PA-17 | Cambiar el monto del presupuesto y la fecha final de una meta | Se recalculan el porcentaje y el plan |
| PA-14 | Con el umbral en 80 % (Configuración), superar el 80 % del total | El resumen muestra la alerta |
| PA-07 | Meta de 1 000 con fin en 14 días | 15 casillas, ninguna negativa |
| PA-08 | Meta de 1 500 | Mensaje: «El monto debe ser un número redondo (múltiplo de 1000)» |
| PA-09 | Marcar los días 1 a 3 y «Guardar días» | Dice «Guardado» y sube el porcentaje |
| PA-13 | Abrir Gráficas y cambiar el período | Los totales coinciden con el resumen |
| PA-15 | Cambiar nombre, moneda y tema; recargar la página | Los cambios siguen ahí |

**Cálculo:** un RF se acepta si todos sus casos se aceptan. Porcentaje = RF aceptados / 20 × 100. La meta es ≥ 90 %.

### 2.3 PU-06 (tarea cronometrada)
Con 5 personas (pueden ser ustedes y conocidos): cada una, sin ayuda, registra un gasto de 25 000 en Alimentación con la descripción «Almuerzo». Se cronometra desde que pulsa «+ Transacción» hasta que el gasto aparece en el resumen, y se anota si lo logró al primer intento. Se llena la tabla de PU-06 del Apéndice G. Se reporta la **mediana** de los 5 tiempos (el del medio, ordenados) y la tasa de éxito (por ejemplo, 5/5).

### 2.4 Pasar los resultados al documento
1. Abrir `docs/latex/resultados.tex`.
2. En las secciones 1 y 2, reemplazar cada `\pendiente{...}` por el resultado. Ejemplo:
   `\newcommand{\resRFAceptados}{19/20 = 95\,\%}`
3. Si repiten alguna herramienta en vivo (sección 3 del archivo), cambiar el texto por el resultado.
4. Guardar la foto del acta firmada en `docs/latex/images/acta_firmada.jpg` y poner en `\resActa`: `ver Figura del acta firmada` (o pedirme que la inserte).
5. Recompilar desde `docs/latex`:
   ```powershell
   latexmk -pdf -shell-escape main.tex
   ```
   Si da error, pídanme que lo compile.

---

## 3. Demostración en vivo del 27 (herramientas y métricas)

Abrir PowerShell en la carpeta del proyecto. Si Windows bloquea los scripts, anteponer `powershell -ExecutionPolicy Bypass -File`.

| Orden | Script | Qué se muestra | Qué decir |
|---|---|---|---|
| 0 | `scripts\demo\00_verificar.ps1` | Que todo está instalado | — |
| 1 | `scripts\demo\01_levantar_app.ps1 -BaseNueva` | La app con datos de prueba (`demo@correo.com` / `Demo12345`) | Presupuesto «Comida del mes» en 117 % (D-04 corregido); reto de $1 000 sin cuotas negativas (D-01) |
| 2 | `scripts\demo\02_pruebas_backend.ps1` | 98 pruebas pytest y el reporte de cobertura en el navegador | 95 % de cobertura; caja negra y blanca; antes había 0 pruebas |
| 3 | `scripts\demo\03_cypress.ps1 -Abrir` | La interfaz de Cypress: elegir `integracion.cy.js` y ver las 8 pruebas | Integración ascendente; 8/8 (antes 7/8, fallaba PI-04) |
| 4 | `scripts\demo\04_selenium.ps1` | Chrome se maneja solo: PA-01, 02, 03, 05, 06 y 08 | Aceptación automatizada; las capturas quedan en `docs/evidencias` |
| 5 | `scripts\demo\05_jmeter.ps1 -Gui` y luego `scripts\demo\05_jmeter.ps1` | El plan (50 usuarios, 60 s, GET y POST) y el reporte HTML | 1 500 peticiones, 0 % de error, p90 de 22 ms (objetivo < 2 s) |
| 6 | `scripts\demo\06_metricas.ps1` | Tamaño con dos herramientas, complejidad, suite CK y estimación | Ninguna función > 10 (antes 3); WMC de las rutas 50 → 7; estimación: puntos de historia 2,05 meses vs. 1,68 reales |
| 7 | `scripts\demo\07_lighthouse.ps1` (y `-Escritorio`) | Reporte de Lighthouse | Accesibilidad 78 → 95; LCP de escritorio 1,4 s |
| 8 | `scripts\demo\08_postgres_pi05.ps1` (opcional) | PI-05 sobre PostgreSQL local | Borrar una categoría con transacciones responde 409 |
| 9 | `scripts\demo\09_zap.ps1` (opcional, Docker) | Escaneo de seguridad | 0 alertas altas |
| 10 | `scripts\demo\10_sonarqube.ps1` (opcional, Docker) | Panel de SonarQube | Calidad y cobertura |

**Consejos:**
- Ejecutar el paso 1 unos 10 minutos antes y dejarlo abierto.
- La primera vez que se abre Cypress tarda en iniciar.
- Para el paso 8, la base debe estar **vacía** (por ejemplo, crear `shiftcash_test` en pgAdmin): las pruebas borran sus tablas.
- ZAP y SonarQube necesitan Docker Desktop encendido. SonarQube tarda unos 2 minutos en arrancar la primera vez, así que conviene prepararlo antes.

---

## 4. Presentación ante jurados (2 de diciembre)

Solo resultados y el programa funcionando.

**Programa:** la app desplegada (<https://shifts-chash-version-amaya.vercel.app>) con una cuenta que ya tenga datos. Si la API de Render no responde, usar la local (`01_levantar_app.ps1`).

**Resultados para mostrar (una diapositiva cada uno):**
- **Problema:** el 53 % de los colombianos no anota sus gastos con regularidad (Asobancaria, 2021).
- **Producto:** 20 requisitos funcionales, 14 casos de uso, desplegado en Vercel, Render y Supabase.
- **Calidad:** 98 pruebas automatizadas, 95 % de cobertura, 15 defectos encontrados (14 corregidos y 1 mitigado).
- **Rendimiento:** 1 500 peticiones con 0 % de error; p90 de 22 ms.
- **Mantenibilidad:** complejidad máxima de 8 (antes, 14); accesibilidad de 95/100.
- **Aceptación:** 20/20 RF aceptados (100 %); PU-06 con mediana de 36 s y 5/5 al primer intento.
- **Estimación:** siete estimaciones (incluidas COSMIC y una herramienta de IA); 2,05 meses estimados frente a 1,68 reales; costo real de $0; valor estimado del trabajo de $15,6 millones.

---

## 5. Problemas frecuentes

| Problema | Solución |
|---|---|
| «No se puede cargar el archivo… la ejecución de scripts está deshabilitada» | Usar `powershell -ExecutionPolicy Bypass -File <script>` |
| La API desplegada no responde | Abrir Supabase: si el proyecto dice *Paused*, pulsar **Restore project** y luego, en Render, **Manual Deploy**. Si no, hacer la demo en local |
| El puerto 8000 o 5173 está ocupado | Cerrar las ventanas de PowerShell minimizadas del paso 1 |
| Cypress o Selenium no encuentran elementos | Verificar que el paso 1 esté corriendo; recargar con `-BaseNueva` |
| JMeter dice que no encuentra Java | Ejecutar `00_verificar.ps1`; el JDK está en `%LOCALAPPDATA%\shiftcash-tools` |

# 💸 ShiftCash - Gestión Financiera

ShiftCash es una aplicación web para el control de finanzas personales: registro de
ingresos y gastos (incluidos los recurrentes), categorías, presupuestos con alerta de
«superado», metas de ahorro con plan de cuotas diarias, gráficas y resumen.

## 🚀 Tecnologías

| Capa | Tecnología |
|---|---|
| Frontend | React 19, Vite, React Router, Recharts, Axios, Google OAuth |
| Backend | Python 3.12, FastAPI, SQLAlchemy 2, Pydantic 2, APScheduler, JWT (python-jose) |
| Base de datos | PostgreSQL (Supabase en producción) |
| Despliegue | Vercel (frontend) y Render (API) |
| Pruebas | pytest + pytest-cov, Cypress, Selenium, Apache JMeter |

Estructura del backend (por capas):

```
backend/app/
├── models.py      # entidades (SQLAlchemy)
├── schemas.py     # validación de entrada/salida (Pydantic)
├── services/      # reglas de negocio (presupuestos, metas, categorías)
├── routes/        # endpoints HTTP (delgados: delegan en services)
├── auth.py        # JWT y usuario actual
└── scheduler.py   # registro diario de transacciones recurrentes
```

## 🛠️ Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/Amaya0910/ShiftCash
cd ShiftCash
```

### 2. Backend (API)

Requisitos: Python 3.12 y una base PostgreSQL (local o Supabase).

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows  (Linux/macOS: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # Linux/macOS: cp .env.example .env
```

Complete `backend/.env` (ver `backend/.env.example`):

| Variable | Uso |
|---|---|
| `DATABASE_URL` | Cadena de conexión de PostgreSQL |
| `SECRET_KEY` | Clave para firmar los JWT |
| `ALGORITHM` | Algoritmo del JWT (`HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Vigencia del token |
| `BACKEND_URL` | URL pública de la API (fotos de perfil) |

Levante la API (las tablas se crean al iniciar):

```bash
uvicorn app.main:app --reload
```

La API queda en http://localhost:8000 y su documentación interactiva en http://localhost:8000/docs.

### 3. Frontend

Requisitos: Node.js 20. Desde la raíz del repositorio:

```bash
npm install
copy .env.example .env.local   # Linux/macOS: cp .env.example .env.local
npm run dev
```

Abra http://localhost:5173. `VITE_API_URL` debe apuntar a la API del paso anterior.

## ✅ Pruebas

```bash
# Unitarias e integración del backend, con cobertura
cd backend
pip install -r requirements-dev.txt
python -m pytest --cov=app --cov-report=term --cov-report=html

# Integración (API + cliente) con Cypress
npx cypress run --env API=<url-api>,SC_EMAIL=<correo>,SC_PASS=<clave>

# Aceptación por la interfaz con Selenium
pip install selenium
python tests/aceptacion_selenium.py      # usa SC_EMAIL, SC_PASS y SC_BASE_URL

# Carga con JMeter (RNF11)
jmeter -n -t tests/carga/shiftcash.jmx -Jtoken=<JWT> -Jcategoria=<id> -l res.jtl -e -o reporte
```

Use siempre una cuenta de prueba: Cypress y JMeter crean registros.

GitHub Actions ejecuta en cada push el lint y la compilación del frontend y las pruebas
del backend con cobertura (`.github/workflows/node.js.yml`). El flujo
`mantener-api-despierta.yml` llama a `/salud` cada 10 minutos: esa ruta consulta la base de datos,
así que ni Render suspende la API ni Supabase pausa la base.

## 🎤 Demostración y presentación

Los scripts de `scripts/demo/` levantan la app con datos de prueba y ejecutan cada herramienta
(pytest, Cypress, Selenium, JMeter, métricas, Lighthouse, ZAP y SonarQube). La guía paso a paso,
con la prueba de aceptación y el orden de la demostración, está en
[docs/GUIA_PRESENTACION.md](docs/GUIA_PRESENTACION.md).

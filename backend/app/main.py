from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routes import users, transactions, categories, budgets, savings, profile
from . import models, scheduler
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ShiftCash API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://shifts-chash-version-amaya.vercel.app",
    ],
    allow_origin_regex=r"https://shifts-chash-version-amaya-.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def cabeceras_de_seguridad(request, call_next):
    """Evita que el navegador adivine el tipo de contenido (alerta baja de ZAP)."""
    respuesta = await call_next(request)
    respuesta.headers["X-Content-Type-Options"] = "nosniff"
    return respuesta


app.include_router(users.router)
app.include_router(profile.router)
app.include_router(transactions.router)
app.include_router(categories.router)
app.include_router(budgets.router)
app.include_router(savings.router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    return {"message": "ShiftCash API funcionando"}
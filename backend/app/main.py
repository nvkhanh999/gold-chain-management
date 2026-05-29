from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from . import models
from .database import engine
from .routers import admin, auth, center, shop


models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Gold Chain Management API")

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ADMIN_DIR = PROJECT_ROOT / "frontend-admin"
CENTER_DIR = PROJECT_ROOT / "frontend-center"
SHOP_DIR = PROJECT_ROOT / "frontend-shop"

app.mount("/static-admin", StaticFiles(directory=str(ADMIN_DIR)), name="static-admin")
app.mount("/static-center", StaticFiles(directory=str(CENTER_DIR)), name="static-center")
app.mount("/static-shop", StaticFiles(directory=str(SHOP_DIR)), name="static-shop")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(center.router)
app.include_router(shop.router)


@app.get("/")
def root():
    return RedirectResponse(url="/admin")


@app.get("/admin")
def adminIndex():
    return FileResponse(ADMIN_DIR / "index.html")


@app.get("/center")
def centerIndex():
    return FileResponse(CENTER_DIR / "index.html")



@app.get("/shop")
def shopIndex():
    return FileResponse(SHOP_DIR / "index.html")

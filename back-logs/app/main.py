from app.db.database import client
from app.docs import tags_metadata
from app.routes.log_data import router as LogDataRouter
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.middleware.gzip import GZipMiddleware
from app.config.settings import settings
from contextlib import asynccontextmanager
from app.routes.health_checks import router as health_router

app = FastAPI(
    title="FastAPI 0.110.2 & Mongo 7",
    description="Api para gestión de logs de auditoría",
    version="1.0.0",
    openapi_tags=tags_metadata,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lógica de inicio    
    yield
    # Lógica de cierre
    client.close()
    
# Middleware para comprimir el response
app.add_middleware(GZipMiddleware, minimum_size=500)

origins = [settings.CORS_ORIGIN]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # type: ignore
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def go_to_docs():
    return RedirectResponse("/docs")

app.include_router(
    LogDataRouter, 
    tags=["log_data"], 
    prefix="/api/v1"
    )

app.include_router(
    health_router, 
    prefix="/api/v1"
)
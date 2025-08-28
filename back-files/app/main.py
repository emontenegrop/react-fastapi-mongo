from contextlib import asynccontextmanager

from app.config.settings import settings
from app.db.database import client
from app.docs import tags_metadata
from app.routes.document_file_upload import router as DocumentFileUploadRouter
from app.routes.file_path import router as FilePathRouter
from app.routes.health_checks import router as health_router
from app.routes.create_token import router as create_token_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse

app = FastAPI(
    title="FastAPI 0.110.0 & Mongo 7",
    description="Api para gestión de archivos con mongodb",
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
    DocumentFileUploadRouter, 
    tags=["document_file"], 
    prefix="/api/v1/document_file"
)
app.include_router(
    FilePathRouter, 
    tags=["file_path"], 
    prefix="/api/v1/file_path"
)
app.include_router(
    health_router, 
    prefix="/api/v1"
)

app.include_router(
    create_token_router, 
    prefix="/api/v1"
)
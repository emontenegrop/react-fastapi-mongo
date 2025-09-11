from contextlib import asynccontextmanager

from app.config.settings import settings
from app.db.database import client
from app.docs import tags_metadata
from app.routes.document_file_upload import router as DocumentFileUploadRouter
from app.routes.file_path import router as FilePathRouter
from app.routes.health_checks import router as health_router
from app.routes.create_token import router as create_token_router
from app.routes.cache import router as cache_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import RedirectResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    from app.utils.mongo_utils import create_indexes
    from app.utils.cache import cache
    
    # Initialize database indexes
    await create_indexes(client[settings.MONGO_DB])
    
    # Initialize Redis cache
    try:
        await cache.initialize()
    except Exception as e:
        # Log but don't fail startup if cache is unavailable
        from app.utils.structured_logger import get_logger
        logger = get_logger("startup")
        logger.warning("Failed to initialize cache, continuing without cache", error=str(e))
    
    yield
    
    # Cleanup logic
    try:
        await cache.close()
    except Exception:
        pass
    client.close()


app = FastAPI(
    title="File Management API",
    description="""
    ## File Management System API
    
    A comprehensive file management system built with FastAPI and MongoDB.
    
    ### Features
    
    * **File Upload & Download**: Upload files with automatic compression and validation
    * **Digital Signature Validation**: Support for digitally signed documents
    * **Path Management**: Configure and manage file storage locations  
    * **Security**: File type validation, size limits, and path traversal protection
    * **Monitoring**: Health checks and comprehensive logging
    * **Authentication**: JWT-based user authentication and authorization
    
    ### File Types Supported
    
    Documents: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, TXT, CSV
    Images: JPG, JPEG, PNG, GIF
    Archives: ZIP
    
    ### Security Features
    
    * File type validation and sanitization
    * Size limits and dangerous file type blocking
    * Path traversal attack prevention
    * Digital signature validation for legal documents
    * JWT token authentication
    * Comprehensive audit logging
    
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
    contact={
        "name": "API Support",
        "email": "support@emtechnology.com",
    },
    license_info={
        "name": "Proprietary",
    },
)


# Cache middleware for automatic response caching
from app.middleware.cache_middleware import CacheMiddleware, CacheInvalidationMiddleware

# Add cache invalidation middleware first (runs last)
app.add_middleware(CacheInvalidationMiddleware)

# Add cache middleware
app.add_middleware(
    CacheMiddleware,
    cacheable_routes={
        "/api/v1/document_file/",
        "/api/v1/file_path/",
        "/api/v1/health/"
    },
    default_ttl=300,  # 5 minutes default cache
    cache_query_params=True
)

# Middleware para comprimir el response
app.add_middleware(GZipMiddleware, minimum_size=500)

# CORS middleware
origins = settings.cors_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # type: ignore
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-User-Name", "X-IP-Address", "X-Event-ID", "X-Application-Code", "X-Cache"],
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

app.include_router(
    cache_router,
    tags=["cache"],
    prefix="/api/v1"
)
"""File validation utilities"""

import os
from typing import List, Optional
from fastapi import UploadFile, HTTPException, status
from app.config.messages import Messages as msg
from app.utils.exceptions import DetailHttpException
from app.schemas.error_content_schema import ErrorContentSchema as Detail


# Configuración de validación de archivos
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB por defecto
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".txt", ".csv", ".zip", ".jpg", ".jpeg", ".png", ".gif"
}
DANGEROUS_EXTENSIONS = {
    ".exe", ".bat", ".cmd", ".com", ".pif", ".scr", ".vbs",
    ".js", ".jar", ".sh", ".ps1", ".php", ".asp", ".jsp"
}


def validate_file_size(file: UploadFile) -> bool:
    """
    Valida el tamaño del archivo.
    
    Args:
        file: Archivo a validar
        
    Raises:
        DetailHttpException: Si el archivo excede el tamaño máximo
        
    Returns:
        bool: True si es válido
    """
    if hasattr(file.file, 'seek'):
        # Obtener tamaño del archivo
        file.file.seek(0, os.SEEK_END)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise DetailHttpException(
                status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                Detail(
                    code="FILE0009",
                    message=f"El archivo excede el tamaño máximo permitido de {MAX_FILE_SIZE / 1024 / 1024:.1f}MB"
                )
            )
    return True


def validate_file_extension(filename: str) -> bool:
    """
    Valida la extensión del archivo.
    
    Args:
        filename: Nombre del archivo
        
    Raises:
        DetailHttpException: Si la extensión no está permitida o es peligrosa
        
    Returns:
        bool: True si es válido
    """
    if not filename:
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            Detail(
                code="FILE0010",
                message="El nombre del archivo es requerido"
            )
        )
    
    # Obtener extensión
    _, ext = os.path.splitext(filename.lower())
    
    # Verificar extensiones peligrosas
    if ext in DANGEROUS_EXTENSIONS:
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            Detail(
                code="FILE0011",
                message=f"Tipo de archivo no permitido: {ext}"
            )
        )
    
    # Verificar extensiones permitidas
    if ext not in ALLOWED_EXTENSIONS:
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            Detail(
                code="FILE0012",
                message=f"Extensión de archivo no soportada: {ext}. Extensiones permitidas: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        )
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitiza el nombre del archivo para evitar path traversal y caracteres problemáticos.
    
    Args:
        filename: Nombre original del archivo
        
    Returns:
        str: Nombre sanitizado del archivo
    """
    if not filename:
        return "unnamed_file"
    
    # Remover path traversal
    filename = os.path.basename(filename)
    
    # Caracteres no permitidos en nombres de archivo
    forbidden_chars = '<>:"/\\|?*'
    for char in forbidden_chars:
        filename = filename.replace(char, '_')
    
    # Remover espacios al inicio y final
    filename = filename.strip()
    
    # Evitar nombres reservados en Windows
    reserved_names = {
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    }
    
    name_without_ext, ext = os.path.splitext(filename)
    if name_without_ext.upper() in reserved_names:
        name_without_ext = f"file_{name_without_ext}"
    
    # Limitar longitud
    max_length = 255
    if len(filename) > max_length:
        name_without_ext = name_without_ext[:max_length - len(ext) - 1]
    
    return f"{name_without_ext}{ext}"


def validate_file(file: UploadFile) -> str:
    """
    Validación completa del archivo.
    
    Args:
        file: Archivo a validar
        
    Returns:
        str: Nombre sanitizado del archivo
    """
    # Validar que el archivo existe
    if not file or not file.filename:
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            Detail(
                code="FILE0013",
                message="No se ha proporcionado ningún archivo"
            )
        )
    
    # Validar extensión
    validate_file_extension(file.filename)
    
    # Validar tamaño
    validate_file_size(file)
    
    # Sanitizar nombre
    sanitized_name = sanitize_filename(file.filename)
    
    return sanitized_name


def validate_content_type(file: UploadFile, allowed_types: Optional[List[str]] = None) -> bool:
    """
    Valida el content-type del archivo.
    
    Args:
        file: Archivo a validar
        allowed_types: Lista de content-types permitidos
        
    Returns:
        bool: True si es válido
    """
    if not allowed_types:
        # Content-types comunes y seguros
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'text/plain',
            'text/csv',
            'application/zip',
            'image/jpeg',
            'image/jpg',
            'image/png',
            'image/gif'
        ]
    
    if file.content_type not in allowed_types:
        raise DetailHttpException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            Detail(
                code="FILE0014",
                message=f"Content-type no permitido: {file.content_type}"
            )
        )
    
    return True
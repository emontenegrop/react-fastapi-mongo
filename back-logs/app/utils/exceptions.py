"""Excepciones personalizadas"""
from fastapi import status
from fastapi import HTTPException
from typing import Any, Dict, Optional

from app.schemas.errro_content_schema import ErrorContentSchema

from app.config.messages import Messages as msg


class DetailHttpException(HTTPException):
    """Excepción HTTP de FatAPI adaptada"""

    def __init__(
        self,
        status_code: int,
        detail: Optional[ErrorContentSchema] = None,
        code: Optional[str] = None,
        message: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Agrega Message o código y message a excepción"""
        if (not code or not message) and not detail:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=msg.INVALID_DETAIL,
            )
        body = detail.model_dump() if detail else {"code": code, "message": message}
        super().__init__(
            status_code=status_code,
            detail=body,
            headers=headers,
        )
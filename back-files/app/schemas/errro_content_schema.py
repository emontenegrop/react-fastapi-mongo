
from pydantic import BaseModel

class ErrorContentSchema(BaseModel):
    """Esquema para mensajes de error"""

    code: str
    message: str
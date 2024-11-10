from app.config.messages import Messages
from app.utils.exceptions import DetailHttpException
from datetime import datetime
from fastapi import APIRouter, status
from app.db.database import db

from app.config.messages import Messages

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", status_code=200)
async def read_current_date_and_time():
    # Crea un documento temporal para obtener la fecha y hora actuales

    temp_doc = {
        "created_at": datetime.now(),
    }
    result = await db.health_check.insert_one(temp_doc)

    # Obtiene el documento que acaba de insertar
    current_date_time = await db.health_check.find_one({"_id": result.inserted_id})

    # Elimina el documento que acaba de insertar
    await db.health_check.delete_one({"_id": current_date_time["_id"]})

    if current_date_time:
        print("__health: ready")
        return {
            "date": current_date_time["created_at"].strftime("%Y-%m-%d"),
            "time": current_date_time["created_at"].strftime("%H:%M:%S"),
        }
    else:
        raise DetailHttpException(
            status.HTTP_424_FAILED_DEPENDENCY, Messages.INVALID_HEALTH_CHECK
        )

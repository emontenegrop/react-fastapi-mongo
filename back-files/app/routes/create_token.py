from fastapi import FastAPI, HTTPException, Depends, status, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import os
from app.middleware.router_error_handler import RouteErrorHandler
from app.config.settings import settings

router = APIRouter(route_class=RouteErrorHandler)


# Configuración
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Modelos Pydantic
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: str
    created_at: datetime
    is_active: bool

class LoginResponse(BaseModel):
    token: str
    user: UserResponse

class ErrorResponse(BaseModel):
    message: str

# Base de datos simulada (en producción usar una BD real)
fake_users_db = {
    "user@example.com": {
        "id": 1,
        "email": "user@example.com",
        "name": "Usuario Ejemplo",
        "role": "user",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        "created_at": datetime.now(),
        "is_active": True
    },
    "admin@example.com": {
        "id": 2,
        "email": "admin@example.com",
        "name": "Administrador",
        "role": "admin",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # password: secret
        "created_at": datetime.now(),
        "is_active": True
    }
}

# Funciones auxiliares
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Genera hash de la contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Verifica y decodifica el token JWT"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )

def get_user_by_email(email: str) -> Optional[dict]:
    """Obtiene un usuario por email"""
    return fake_users_db.get(email)

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Autentica un usuario"""
    user = get_user_by_email(email)
    if not user:
        return None
    if not verify_password(password, user["hashed_password"]):
        return None
    return user

# Endpoints
@router.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """
    Endpoint de login que devuelve token JWT y datos del usuario
    """
    # Autentica el usuario
    user = authenticate_user(login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Usuario inactivo"
        )
    
    # Crea el token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": user["id"]},
        expires_delta=access_token_expires
    )
    
    # Prepara los datos del usuario para la respuesta
    user_response = UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )
    
    return LoginResponse(
        token=access_token,
        user=user_response
    )

@router.get("/auth/me", response_model=UserResponse)
async def get_current_user(token_data: dict = Depends(verify_token)):
    """
    Endpoint para obtener información del usuario actual
    """
    email = token_data.get("sub")
    user = get_user_by_email(email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    return UserResponse(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        role=user["role"],
        created_at=user["created_at"],
        is_active=user["is_active"]
    )

@router.post("/auth/logout")
async def logout(token_data: dict = Depends(verify_token)):
    """
    Endpoint de logout (en el cliente se debe eliminar el token)
    """
    return {"message": "Logout exitoso"}

@router.get("/auth/refresh", response_model=dict)
async def refresh_token(token_data: dict = Depends(verify_token)):
    """
    Endpoint para renovar el token
    """
    email = token_data.get("sub")
    user_id = token_data.get("user_id")
    
    # Crea un nuevo token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_token = create_access_token(
        data={"sub": email, "user_id": user_id},
        expires_delta=access_token_expires
    )
    
    return {"token": new_token}

# Endpoint de salud
@router.get("/health")
async def health_check():
    """Endpoint para verificar el estado del servidor"""
    return {"status": "ok", "timestamp": datetime.now()}


from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    GoogleLoginRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


def _bearer_token(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return auth_header.split(" ", 1)[1]


@router.get("/config")
def auth_config():
    """Public auth UI config (no secrets)."""
    from app.config import settings

    return {
        "google_enabled": bool(settings.GOOGLE_CLIENT_ID),
        "token_expire_minutes": settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    }


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return AuthService.register_user(db, user_data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        return AuthService.login_user(db, login_data)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


@router.post("/google-login", response_model=TokenResponse)
def google_login(request_body: GoogleLoginRequest, db: Session = Depends(get_db)):
    try:
        return AuthService.google_login(
            db,
            google_id=request_body.google_id,
            email=request_body.email,
            full_name=request_body.full_name,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    token = _bearer_token(request)
    AuthService.logout(db, token)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
def me(request: Request, db: Session = Depends(get_db)):
    token = _bearer_token(request)
    try:
        user = AuthService.get_current_user(db, token)
        return UserResponse.model_validate(user)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc


def get_optional_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Optional auth helper for routes that work with or without a logged-in user."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ", 1)[1]
    try:
        return AuthService.get_current_user(db, token)
    except ValueError:
        return None

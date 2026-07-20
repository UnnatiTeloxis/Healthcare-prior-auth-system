from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User, UserSession
from app.schemas.user import UserCreate, UserLogin, UserResponse


class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> UserResponse:
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise ValueError("Email already registered")

        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            full_name=user_data.full_name,
            is_verified=False,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return UserResponse.model_validate(user)

    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> dict:
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user or not verify_password(login_data.password, user.password_hash):
            raise ValueError("Invalid email or password")
        if not user.is_active:
            raise ValueError("Account is deactivated")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        user.last_login = now
        user.login_count = (user.login_count or 0) + 1
        db.commit()
        db.refresh(user)

        token = create_access_token({"sub": str(user.id), "email": user.email})
        session = UserSession(
            user_id=user.id,
            token=token,
            expires_at=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        db.add(session)
        db.commit()

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": UserResponse.model_validate(user),
        }

    @staticmethod
    def google_login(
        db: Session,
        *,
        google_id: str,
        email: str,
        full_name: str | None = None,
    ) -> dict:
        user = db.query(User).filter(User.google_id == google_id).first()
        if not user:
            user = db.query(User).filter(User.email == email).first()
            if user:
                user.google_id = google_id
            else:
                user = User(
                    email=email,
                    password_hash="",
                    full_name=full_name,
                    google_id=google_id,
                    is_verified=True,
                    is_active=True,
                )
                db.add(user)

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        user.last_login = now
        user.login_count = (user.login_count or 0) + 1
        db.commit()
        db.refresh(user)

        token = create_access_token({"sub": str(user.id), "email": user.email})
        session = UserSession(
            user_id=user.id,
            token=token,
            expires_at=now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        db.add(session)
        db.commit()

        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": UserResponse.model_validate(user),
        }

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        payload = decode_token(token)
        if not payload:
            raise ValueError("Invalid token")

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("Invalid token payload")

        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise ValueError("User not found")
        if not user.is_active:
            raise ValueError("User is deactivated")

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        session = (
            db.query(UserSession)
            .filter(
                UserSession.token == token,
                UserSession.expires_at > now,
            )
            .first()
        )
        if not session:
            raise ValueError("Session expired")

        return user

    @staticmethod
    def logout(db: Session, token: str) -> bool:
        session = db.query(UserSession).filter(UserSession.token == token).first()
        if not session:
            return False
        db.delete(session)
        db.commit()
        return True

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)

    def register(self, data: RegisterRequest) -> User:
        if self.users.get_by_email(data.email.lower()) is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        return self.users.create(data, hash_password(data.password))

    def login(self, data: LoginRequest) -> str:
        user = self.users.get_by_email(data.email.lower())
        if user is None or not verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user cannot authenticate")
        return create_access_token(subject=str(user.id))
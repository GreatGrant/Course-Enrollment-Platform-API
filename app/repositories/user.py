from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import RegisterRequest


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))

    def create(self, data: RegisterRequest, hashed_password: str) -> User:
        user = User(
            name=data.name,
            email=data.email.lower(),
            hashed_password=hashed_password,
            role=data.role,
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_all(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.id)).all())
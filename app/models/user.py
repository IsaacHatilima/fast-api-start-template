import uuid

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    public_id = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        index=True,
    )

    email = Column(String, unique=True, index=True, nullable=False)
    email_verified_at = Column(DateTime(timezone=True), nullable=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    profile = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        single_parent=True,
    )

    def __repr__(self):
        return f"<User id={self.id} public_id={self.public_id} email={self.email}>"

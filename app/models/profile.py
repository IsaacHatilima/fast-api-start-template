import uuid

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.session import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    public_id = Column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship(
        "User",
        back_populates="profile",
    )

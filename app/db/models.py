from sqlalchemy import Table, Column, Integer, String, ForeignKey, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.config.db import Base

# tabela de associação N:N (User <-> Challenge)
user_challenge = Table(
    "user_challenge",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("challenge_id", Integer, ForeignKey("challenge.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    # 1:N (User -> CheckIn)
    checkins = relationship(
        "CheckIn", back_populates="user", cascade="all, delete-orphan"
    )

    # N:N (User <-> Challenge)
    challenge = relationship(
        "Challenge", secondary=user_challenge, back_populates="users"
    )


class CheckIn(Base):
    __tablename__ = "checkins"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="checkins")


class Challenge(Base):
    __tablename__ = "challenge"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    start_date = Column(String, nullable=False)

    users = relationship("User", secondary=user_challenge, back_populates="challenge")

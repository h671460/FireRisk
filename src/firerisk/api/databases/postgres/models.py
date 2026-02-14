from src.firerisk.api.databases.postgres.database import POSTGRES_Base
from sqlalchemy import Column, Integer, String, DateTime, func

class Users(POSTGRES_Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(255), unique=True, nullable=False)

    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)

    hashed_password = Column(String(255), nullable=False)

    role = Column(String(50), nullable=False, server_default="user")

    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())

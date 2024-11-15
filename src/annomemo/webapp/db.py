import os
from sqlmodel import SQLModel, Field, Session
from typing import Optional

from sqlalchemy import create_engine

_dburi = os.getenv('SQLALCHEMY_DATABASE_URI')


if _dburi is None:
    raise RuntimeError('env var SQLALCHEMY_DATABASE_URI not set')

engine = create_engine(_dburi)


class User(SQLModel):
    id: Optional[int] = Field(primary_key=True, default=None)
    email: str = Field(unique=True)


class UserInDB(User, table=True):
    __tablename__: str = "users"
    password: str = Field()

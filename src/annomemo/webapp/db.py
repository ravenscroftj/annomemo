import email
import os
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from sqlmodel import SQLModel, Field
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

    @classmethod
    def from_email_and_password(cls, email: str, password: str) -> 'UserInDB':

        hasher = PasswordHash(hashers=[Argon2Hasher()])

        return cls(email=email, password=hasher.hash(password))

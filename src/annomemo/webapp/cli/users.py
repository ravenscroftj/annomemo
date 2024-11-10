from argon2 import PasswordHasher
import click
import pwdlib

from annomemo.webapp.db import engine, UserInDB

from sqlalchemy.orm import create_session

from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib import PasswordHash


@click.group(name="users")
def users():
    """Manage users in the platform"""


@users.command(name="add")
@click.option("--email", prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
def add_user(email, password):
    """create a new user"""

    session = create_session(engine)

    hasher = PasswordHash(hashers=[Argon2Hasher()])

    # see if user with this email already exists
    session.query(UserInDB).filter_by(email=email).first()

    if session.query(UserInDB).filter_by(email=email).count():
        raise ValueError(f"User with email {email} already exists")

    user = UserInDB.from_email_and_password(email, password)
    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        print(f"User {email} (id={user.id}) created")
    except Exception as e:
        print("Error creating user:", str(e))

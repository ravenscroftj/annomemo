from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from annomemo.webapp.schemas.auth import RegistrationForm
from ..db import User, UserInDB, engine
from sqlmodel import Session

from loguru import logger


def create_user(reg_form: RegistrationForm):

    with Session(engine) as session:

        hasher = PasswordHash(hashers=[Argon2Hasher()])

        user = UserInDB(fullName=reg_form.fullName, email=reg_form.email,
                        password=hasher.hash(reg_form.password))

        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"User with id={user.id} and email={
                    user.email} was created")
        # cast to normal user to remove password property
        return User(**user.__dict__)

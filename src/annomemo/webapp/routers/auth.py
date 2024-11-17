
from annomemo.webapp.schemas.auth import RegistrationForm
from annomemo.webapp.services.auth import create_user
from ..main import app, templates
from ..db import UserInDB

from loguru import logger

from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core import ValidationError
from typing import Annotated
from fastapi import APIRouter, Request, Form, HTTPException

from sqlalchemy.exc import IntegrityError
from sqlite3 import IntegrityError as SQLiteIntegrityError

authapi = APIRouter(prefix="/auth", tags=['auth'])


@authapi.get("/register")
async def register_form(req: Request):
    """Display registration form"""

    return templates.TemplateResponse(req, "auth/register.html", {"errors": {}})


@authapi.post(
    "/register",
)
async def register_payload(req: Request):
    """Handle form submission, display any errors and then register user"""

    raw_data = await req.form()

    context: dict[str, str | dict] = {key: value for key, value in raw_data.items() if key in [
        'fullName', 'email']}  # type: ignore
    try:
        reg_form = RegistrationForm(**raw_data)  # type: ignore
        user = create_user(reg_form)
        return templates.TemplateResponse(req, "auth/register_success.html", {"user": user})

    except ValidationError as e:

        logger.warning(e)

        context['errors'] = {err["loc"][0]: err["msg"] for err in e.errors()}

        return templates.TemplateResponse(
            req,
            "auth/register.html",
            context,
        )

    except (IntegrityError, SQLiteIntegrityError) as e:

        logger.warning(e)

        context['errors'] = {
            "email": "A user with this email already exists, If this is you <a href='/auth/login'>Log in</a>"}

        return templates.TemplateResponse(
            req,
            "auth/register.html",
            context
        )

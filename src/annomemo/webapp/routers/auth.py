from annomemo.webapp.schemas.auth import RegistrationForm
from annomemo.webapp.services.auth import create_user
from ..main import app, templates
from ..db import UserInDB

from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core import ValidationError
from typing import Annotated
from fastapi import APIRouter, Request, Form, HTTPException

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
    try:
        reg_form = RegistrationForm(**raw_data)  # type: ignore
        user = create_user(reg_form)
        return templates.TemplateResponse("auth/register_success.html", {"user": user})

    except ValidationError as e:
        return templates.TemplateResponse(
            req,
            "auth/register.html",
            {"errors": {err["loc"][0]: err["msg"] for err in e.errors()}},
        )

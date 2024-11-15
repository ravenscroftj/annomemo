from ..app import app, templates
from ..db import UserInDB

from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core import ValidationError
from typing import Annotated
from fastapi import APIRouter, Request, Form, HTTPException

authapi = APIRouter()


class RegistrationForm(BaseModel):
    fullName: str
    email: EmailStr
    password: str = ...
    confirmPassword: str

    @field_validator("password")
    @classmethod
    def pw_not_blank(cls, v, info):
        """validate that the password field is at least 8 chars long"""
        if v is None or len(v) < 8:
            raise ValueError("Passwords must be at least 8 characters long")

        return v

    @field_validator("confirmPassword")
    @classmethod
    def passwords_match(cls, v, info):
        if v != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return v


@authapi.get("/register")
async def register_form(req: Request):
    """Display registration form"""

    return templates.TemplateResponse(req, "register.html", {"errors": {}})


@authapi.post(
    "/register",
)
async def register_payload(req: Request):
    """Handle form submission, display any errors and then register user"""

    raw_data = await req.form()
    try:
        reg_form = RegistrationForm(**raw_data)

    except ValidationError as e:
        return templates.TemplateResponse(
            req,
            "register.html",
            {"errors": {err["loc"][0]: err["msg"] for err in e.errors()}},
        )

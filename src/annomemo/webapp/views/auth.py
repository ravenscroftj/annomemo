from ..app import app, templates
from ..db import UserInDB

from pydantic import BaseModel, EmailStr, field_validator
from typing import Annotated
from fastapi import APIRouter, Request, Form

authapi = APIRouter()


class RegistrationForm(BaseModel):
    fullName: str
    email: EmailStr
    password: str
    confirmPassword: str

    @field_validator('confirmPassword')
    def passwords_match(cls, v, info):
        if v != info.data.get('password'):
            raise ValueError('Passwords do not match')
        return v


@authapi.get("/register")
async def register_form(req: Request):
    """Display registration form"""

    return templates.TemplateResponse(req, "register.html", {"errors": {}})


@authapi.post("/register", )
async def register_payload(req: Request, form: Annotated[RegistrationForm, Form()]):

    return

from ..app import app, templates
from ..db import UserInDB

from pydantic import BaseModel
from typing import Annotated
from fastapi import APIRouter, Request, Form

authapi = APIRouter()


class RegistrationForm(BaseModel):
    email: str
    password: str


@authapi.get("/register")
async def register_form(req: Request):
    """Display registration form"""

    return templates.TemplateResponse(req, "register.html", {})


@authapi.post("/register", )
async def register_payload(req: Request, form: Annotated[RegistrationForm, Form()]):

    return

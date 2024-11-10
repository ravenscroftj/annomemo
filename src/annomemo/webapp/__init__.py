from . import views
from .app import app
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Request
from fastapi import FastAPI
from dotenv import load_dotenv


load_dotenv()

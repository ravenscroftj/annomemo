from ..app import app, templates

from .auth import authapi

app.mount("/auth", authapi)


@app.route("/")
async def index(req):
    return templates.TemplateResponse(req, "landing.html", context={})

from ..main import app, templates

from .auth import authapi

app.include_router(authapi)


@app.route("/")
async def index(req):
    return templates.TemplateResponse(req, "landing.html", context={})

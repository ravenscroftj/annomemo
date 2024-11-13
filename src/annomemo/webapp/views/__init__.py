from ..app import app, templates

from . import auth


@app.route("/")
async def index(req):
    return templates.TemplateResponse(req, "landing.html", context={})

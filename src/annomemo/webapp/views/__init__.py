from ..app import app, templates


@app.route('/')
async def index(req):
    return templates.TemplateResponse(req, 'main.html', context={})

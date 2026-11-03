# python -m uvicorn main:app --reload

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse



# app = FastAPI()
# app.mount('/static', StaticFiles(directory='static'), name='static')
# temaplates = Jinja2Templates(directory='templates')

# # white_urls = ['/']

# @app.get('/',response_class=HTMLResponse)
# def main_page(request:Request):
#     return temaplates.TemplateResponse(request=request, name='index.html')



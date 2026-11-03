from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse


app = FastAPI()
app.mount('/static', StaticFiles(directory='SecondPractice/static'), name='static')
templates = Jinja2Templates(directory='SecondPractice/templates')


@app.get('/home', response_class=HTMLResponse)
@app.get('/', response_class=HTMLResponse)
def home(request:Request):
    session_id = request.cookies.get('session_id')
    print(session_id)
    return templates.TemplateResponse(request=request, name='home.html')

@app.get('/403', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='403.html')
    
@app.get('/404', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='404.html')
    
@app.get('/login', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='login.html')
    
@app.get('/register', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='register.html')
    
@app.get('/catalog', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='catalog.html')
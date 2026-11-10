from fastapi import FastAPI, Form, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from classForApp import Functions
import uuid
from datetime import datetime, timedelta


func = Functions()
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')
active_sessions = {}


@app.middleware('http')
async def dsiableCache(request:Request, call_next):
    response : Response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


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

@app.post('/login')
def postLogin(request:Request, email: str = Form(...), password: str = Form(...)):
    digits = func.getCollumn()
    hexPassword = func.getHexPassword(password)
    if email in digits[1].values and hexPassword in digits[3].values:
        session_id = str(uuid.uuid4())
        active_sessions[session_id] = datetime.now()
        response = RedirectResponse(url='/catalog', status_code=303)
        response.set_cookie(key='session_id', value=session_id, httponly=True, secure=True, samesite='lax')
        response.set_cookie(key='email', value=email, httponly=True, secure=True, samesite='lax')
        return response
    else:
        error = 'Неправильный email или пароль'
        return templates.TemplateResponse(request=request, name='login.html', context={'error' : error})


@app.get('/login', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='login.html')

@app.post('/register')
def postRegister(request:Request, name : str = Form(...), email : str = Form(...), password : str = Form(...)):
    func.writeCharacteristics(name, email, password)
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = datetime.now()
    response = RedirectResponse(url='/catalog', status_code=303)
    response.set_cookie(key='session_id', value=session_id, httponly=True, secure=True, samesite='lax')
    return response

@app.get('/register', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='register.html')
    
@app.get('/catalog', response_class=HTMLResponse)
def home(request:Request, email : str = Cookie(default='User')):
    session_id = request.cookies.get('session_id')
    if session_id in active_sessions.keys():
        return templates.TemplateResponse(request=request, name='catalog.html', context={'email' : email})
    else:
        return templates.TemplateResponse(request=request, name='403err.html')

@app.get('/logout', response_class=HTMLResponse)
def logout(request:Request):
    session_id = request.cookies.get('session_id')
    if session_id in active_sessions.keys():
        del active_sessions[session_id]
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie(key='session_id')
    response.delete_cookie(key='email')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

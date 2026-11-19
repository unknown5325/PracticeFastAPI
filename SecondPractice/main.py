from fastapi import FastAPI, Form, Cookie, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from starlette.middleware.sessions import SessionMiddleware
from classForApp import Functions
import uuid
from datetime import datetime, timedelta
from urllib.parse import quote, unquote
from pathlib import Path
import pandas as pd
import random
import os
import random


ACTIVETIME = timedelta(hours=30)

func = Functions()
app = FastAPI()
app.mount('/static', StaticFiles(directory='static'), name='static')
app.mount('/static/avatars', StaticFiles(directory='static/avatars'), name='static/avatars')
app.add_middleware(SessionMiddleware, secret_key='checkHowItWorks') # добавление midlleware для создания сессий
templates = Jinja2Templates(directory='templates')
df = pd.read_csv('sessions.csv')
ses = df['session_id']
tm = df['time']
active_sessions = dict(zip(ses, tm))

UPLOAD_DIR = Path("static/avatars")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.middleware('http')
async def dsiableCache(request:Request, call_next):
    response : Response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get('/home', response_class=HTMLResponse)
def home(request:Request):
    try:
        time = request.cookies.get('time')
        dt_time = datetime.fromisoformat(time)
        if datetime.now() - dt_time < ACTIVETIME:
            role = request.cookies.get('role')
            name = request.cookies.get('name')
            logo = request.cookies.get('logo')
            return templates.TemplateResponse(request=request, name='home.html', context={'name' : name, 'role' : role, 'logo' : logo})
        else:
            return templates.TemplateResponse(request=request, name='403err.html')
    except Exception:
        return templates.TemplateResponse(request=request, name='403err.html')

@app.get('/403', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='403.html')
    
@app.get('/404', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='404.html')

@app.post('/')
@app.post('/login')
def postLogin(request:Request, email: str = Form(...), password: str = Form(...)):
    digits = func.getCollumn()
    hexPassword = func.getHexPassword(password)
    if email in digits[1].values and hexPassword in digits[3].values:
        df = pd.read_csv('UserList.csv', index_col='Email')
        user_row = df.loc[f'{email}']
        logo = user_row['img']
        name = user_row['Name']
        role = user_row['Role']
        session_id = str(uuid.uuid4())
        active_sessions[session_id] = datetime.now()
        response = RedirectResponse(url='/catalog', status_code=303)
        response.set_cookie(key='session_id', value=session_id, httponly=True, secure=True, samesite='lax')
        # request.session['session_id'] = session_id
        response.set_cookie(key='name', value=name, httponly=True, secure=True, samesite='lax')
        # request.session['email'] = email
        response.set_cookie(key='time', value=active_sessions[session_id], httponly=True, secure=True, samesite='lax')
        # request.session['time'] = active_sessions[session_id] Не работает с типами данных datetime
        response.set_cookie(key='logo', value=logo, httponly=True, secure=True, samesite='lax')
        # request.session['logo'] = logo
        response.set_cookie(key='role', value=role, httponly=True, secure=True, samesite='lax')
        # request.session['role'] = role
        func.writeLogs(email, session_id, active_sessions[session_id]) # для создания файла с сессиями
        return response
    else:
        error = 'Неправильный email или пароль'
        return templates.TemplateResponse(request=request, name='login.html', context={'error' : error})

@app.get('/', response_class=HTMLResponse)
@app.get('/login', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='login.html')

@app.post('/register')
async def postRegister(request:Request, name : str = Form(...), email : str = Form(...), password : str = Form(...), img : UploadFile = File(...)):
    session_id = str(uuid.uuid4())
    active_sessions[session_id] = datetime.now()

    file_ext = Path(img.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = UPLOAD_DIR / unique_filename

    content = await img.read()
    with open(file_path, "wb") as f:
        f.write(content)

    roles = ['Observer', 'Admin', 'Moderator']
    role = random.choice(roles)

    func.writeCharacteristics(name, email, password, unique_filename, role)
    response = RedirectResponse(url='/catalog', status_code=303)
    response.set_cookie(key='session_id', value=session_id, httponly=True, secure=True, samesite='lax')
    # request.session['session_id'] = session_id
    response.set_cookie(key='time', value=active_sessions[session_id], httponly=True, secure=True, samesite='lax')
    # request.session['time'] = active_sessions[session_id] не работают с типами данных datetime
    response.set_cookie(key='logo', value=unique_filename)
    # request.session['email'] = email
    response.set_cookie(key='name', value=name)
    # request.session['role'] = role
    response.set_cookie(key='role', value=role)
    func.writeLogs(email, session_id, active_sessions[session_id]) # для создания файла с сессиями
    return response



@app.get('/register', response_class=HTMLResponse)
def home(request:Request):
    return templates.TemplateResponse(request=request, name='register.html')

@app.post('/catalog')
def getCatalog(request:Request, 
            header: str = Form(default=''), 
            news: str = Form(default=''),
            id: str = Form(default='')):
    name = request.cookies.get('name')
    logo = request.cookies.get('logo')
    response = RedirectResponse(url='/catalog', status_code=303)
    df = pd.DataFrame({'avatar' : logo, 'name' : name, 'header' : header, 'news' : news, 'id' : id}, index=[0])
    df.to_csv('NewsList.csv', index=False,  mode="a", sep=",", header=not os.path.isfile("NewsList.csv"))
    return response
    
@app.get('/catalog', response_class=HTMLResponse)
def catalog(request:Request, name : str = Cookie(default='User')):
    try:
        session_id = request.cookies.get('session_id')
        time = request.cookies.get('time')
        logo = request.cookies.get('logo')
        name = request.cookies.get('name')
        role = request.cookies.get('role')
        print(time)
        dt_time = datetime.fromisoformat(time)
        if session_id in active_sessions.keys() and datetime.now() - dt_time < ACTIVETIME: # Добавление времени сессии
            return templates.TemplateResponse(request=request, name='catalog.html', context={'name' : name, 'logo' : logo, 'role' : role})
        else:
            del active_sessions[session_id]
            return templates.TemplateResponse(request=request, name='403err.html')
    except Exception as e:
        print(e)
        return templates.TemplateResponse(request=request, name='403err.html')


@app.get('/form', response_class=HTMLResponse)
def form(request:Request, name: str = Cookie(default='User'), id : str = '', dtype={'id': str}):
    try:
            session_id = request.cookies.get('session_id')
            time = request.cookies.get('time')
            logo = request.cookies.get('logo')
            name = request.cookies.get('name')
            role = request.cookies.get('role')

            df = pd.read_csv('NewsList.csv', index_col='id', dtype=str)
            user_row = df.loc[id]
            nameNews = user_row['name']
            avatarNews = user_row['avatar']
            headerNews = user_row['header']
            news = user_row['news']


            dt_time = datetime.fromisoformat(time)
            if session_id in active_sessions.keys() and datetime.now() - dt_time < ACTIVETIME: # Добавление времени сессии
                return templates.TemplateResponse(request=request, name='form.html', context={'name' : name, 
                                                                                              'logo' : logo, 
                                                                                              'role' : role, 
                                                                                              'header' : headerNews, 
                                                                                              'nameNews' : nameNews, 
                                                                                              'avatarNews' : avatarNews,
                                                                                              'news' : news,
                                                                                              'id' : id})
            else:
                print('bad')
                del active_sessions[session_id]
                return templates.TemplateResponse(request=request, name='403err.html')
    except Exception as e:
            print(e)
            return templates.TemplateResponse(request=request, name='403err.html')


@app.get('/logout', response_class=HTMLResponse)
def logout(request:Request):
    session_id = request.cookies.get('session_id')
    if session_id in active_sessions.keys():
        del active_sessions[session_id]
    response = RedirectResponse(url='/login', status_code=303)
    response.delete_cookie(key='session_id')
    response.delete_cookie(key='email')
    response.delete_cookie(key='time')
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    func.reWriteLogs(session_id) # перезапись файла sessions с удалением
    return response

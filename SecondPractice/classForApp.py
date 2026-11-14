import pandas as pd
import hashlib
import os
import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, Form, Cookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response


class Functions:

    def __init__(self):
        self.templates = Jinja2Templates(directory='templates')

    def getHexPassword(self, password):
        hex_obj = hashlib.sha256(password.encode('utf-8'))
        hex_dig = hex_obj.hexdigest()
        return hex_dig

    def writeCharacteristics(self, name, email, password, img, role):
        hexDig = self.getHexPassword(password)
        df = pd.DataFrame({'Name' : name, 'Email' : email, 'Password' : password, 'HashPassword' : hexDig, 'img' : img, 'Role' : role}, index=[0])
        df.to_csv('UserList.csv', index=False,  mode="a", sep=",", header=not os.path.isfile("UserList.csv"))

    def getCollumn(self):
        df = pd.read_csv('UserList.csv')
        nameCollumn = df['Name']
        emailCollumn = df['Email']
        passwordCollumn = df['Password']
        hexPasswordCollumn = df['HashPassword']
        imgCollumn = df['img']
        return nameCollumn, emailCollumn, passwordCollumn, hexPasswordCollumn, imgCollumn

    def createSession(self, acts: dict):
        session_id = str(uuid.uuid4())
        acts[session_id] = datetime.now()
        return session_id

    def writeLogs(self, email, session_id, time):
        df = pd.DataFrame({ 'Email' : email, 'session_id' : session_id, 'time' : time }, index=[0])
        df.to_csv('sessions.csv', index=False,  mode="a", sep=",", header=not os.path.isfile("sessions.csv"))

    def reWriteLogs(self, session_id):
        df = pd.read_csv('sessions.csv')
        df = df[df['session_id'] != session_id]
        df.to_csv('sessions.csv', index=False)

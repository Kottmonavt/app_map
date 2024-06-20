import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI
from gotrue.errors import AuthApiError
from pydantic import BaseModel
from math import *

load_dotenv()

url: str = "https://dxbgcjyicfxyhizutaiz.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR4YmdjanlpY2Z4eWhpenV0YWl6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MTc4NjgzMTEsImV4cCI6MjAzMzQ0NDMxMX0.OpGnfFvMsHO56MyUspLmnFpVnRHFuxIqbemJpnMUYQE"
supabase: Client = create_client(url, key)

app = FastAPI()


@app.get("/")
async def home():
    return {"data": "based"}


class User(BaseModel):
    login: str
    password: str 


class warningZone(BaseModel):
    xCoord: float
    yCoord: float
    typeZone: str
    distance: float


class userPosition(BaseModel):
    xCoord: float
    yCoord: float


class userInfo(BaseModel):
    user: str
    currentSpeed: float
    xCoord: float
    yCoord: float
    allowedSpeed: float


# Регистрация пользователя
@app.post("/users/sign-up")
async def create_user(user: User):
    
    credentials = {
    "email": user.login,
    "password": user.password
    }
    
    # TODO добавить обработку различных исключение при регистрации
    try:
        user, session = supabase.auth.sign_up(credentials)
    except AuthApiError as e:
        return AuthApiError.to_dict(e)

    res = {'status': 200,
           'user': user[1]}
    

    return res


@app.post("/users/sign-out")
async def log_out():
    res = supabase.auth.sign_out()

    return {"status": 200}


# Вход пользователя
@app.post("/users/sign-in")
async def get_user(user: User):

    credentials = {
    "email": user.login,
    "password": user.password
    }

    # TODO добавить обработку различных исключение при входе пользователя
    try:
        user, session = supabase.auth.sign_in_with_password(credentials)
    except AuthApiError as e:
        return AuthApiError.to_dict(e)

    res = {'status': 200,
           'user': user[1]}

    return res


# добавление записи об опасной зоне
@app.post("/warningZone/add")
async def addWarningZone(warningZone: warningZone):
    x_p = warningZone.xCoord + warningZone.distance
    x_m = warningZone.xCoord - warningZone.distance
    y_p = warningZone.yCoord + warningZone.distance
    y_m = warningZone.yCoord - warningZone.distance
    data_coord = supabase.table('warningZone').insert({"xCoord": warningZone.xCoord, "yCoord": warningZone.yCoord, "typeZone": warningZone.typeZone, "distance": warningZone.distance,"x_p": x_p, "x_m": x_m, "y_p": y_p, "y_m": y_m}).execute()
    assert len(data_coord.data) > 0


@app.post("/warningZone/get")
async def getWarningZone(userPosition: userPosition):
    data = supabase.table('warningZone').select("*", count='exact').filter('x_p', 'gte', userPosition.xCoord).filter('x_m', 'lte', userPosition.xCoord).filter('y_p', 'gte', userPosition.yCoord).filter('y_m', 'lte', userPosition.yCoord).execute()
    if data.count > 0:
        return data
    else:
        res = {'status': 200}
        return res
    

@app.post("/userInfo/add")
async def addUserInfo(userInfo: userInfo):
    data = supabase.table("userInfo").insert({"user": userInfo.user, "currentSpeed": userInfo.currentSpeed, "xCoord": userInfo.xCoord, "yCoord": userInfo.yCoord, "allowedSpeed": userInfo.allowedSpeed}).execute()
    assert len(data.data) > 0
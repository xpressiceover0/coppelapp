# servidor
import uvicorn

# framework
from fastapi import FastAPI, Body, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

from typing import List


#Database
from db import config

# misc
import requests as rq
import json
import time
import datetime
import os
import subprocess
import re
import uuid
from decouple import config #import dotenv -> en caso de manejar strings como variables de entorno
from cryptography.fernet import Fernet


# _______________________________ INSTANCIA DE APP _______________________________
# La clase fastApi inicia los endpionts de la api
app=FastAPI()

# añadir a allow_origins los dominios válidos para evitar ataques de cross origin 
app.add_middleware(CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'])

async def get(url):
    return rq.get(url)

# _______________________________ LLAVE DE ACCESO DE APP _______________________________
key=config('key')
fnt=Fernet(bytes(key, encoding='utf-8'))

#___________________________________ ENDPOINTS ___________________________________

@app.post("/search", status_code=200)
async def search(password=Header(...), search_query: str = Body(...)):
    
    if fnt.decrypt(bytes(config('pass'), encoding='utf-8')) == bytes(password, encoding='utf-8'):
        url=f'http://api.tvmaze.com/search/shows?q={search_query}'
        r = await get(url)
        
        if r.status_code==200:
            contents=json.loads(r.text)
            
            response=[
                {
                'id': content['show']['id'], 
                'name': content['show']['name'],
                'channel': content['show']['webChannel'] or content['show']['network']['name'],
                'summary': content['show']['summary'],
                'genres': content['show']['genres']}

                for content in contents if content['show']]
            
            return response
        
        else:
            raise HTTPException(status_code=r.status_code, detail="Error de api")
    else:
        raise HTTPException(status_code=404, detail="Token invalido o expirado")


#___________________________________ ENTRY POINT ___________________________________
if __name__=='__main__':
    uvicorn.run(app, host='0.0.0.0', port=config('PORT', cast=int))
# servidor
import uvicorn

# framework
from fastapi import FastAPI, Body, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

from typing import List


#Database
from db.config import client

# misc
import requests as rq
import json
import sys
from decouple import config #import dotenv -> en caso de manejar strings como variables de entorno
from cryptography.fernet import Fernet


# _______________________________ CONEXION DB _______________________________
db=client[config('schema')]

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
    

@app.post("/show", status_code=200)
async def show(password=Header(...), show_id: int = Body(...)):
    
    if fnt.decrypt(bytes(config('pass'), encoding='utf-8')) == bytes(password, encoding='utf-8'):
        
        table=db['show_cache']
        query = { "_id": show_id }

        cursor = table.find_one(query)
        
        if cursor:
            return cursor
        
        else:
            url=f'https://api.tvmaze.com/shows/{show_id}'
            r = await get(url)
            
            if r.status_code==200:
                response=json.loads(r.text)
                response['_id']=response.pop('id')
                try:
                    db_response=table.insert_one(response)
                    if not db_response.acknowledged:
                        print('ERROR DB acknowledged false /show')
                        # no se levanta excepcion porque no es indispensable insertar en cache mientras la API funcione

                except:
                    print('ERROR DB insert API response onject /show ')
                
                return response
            
            else:
                raise HTTPException(status_code=r.status_code, detail="Error de api")
    else:
        raise HTTPException(status_code=404, detail="Token invalido o expirado")


@app.post("/comments", status_code=201)
async def show(password=Header(...), show_id: int = Body(...), comment: str = Body(...), rating: int = Body(...)):
    
    if fnt.decrypt(bytes(config('pass'), encoding='utf-8')) == bytes(password, encoding='utf-8'):
        
        table=db['comments_rating']

        opinion = {"comment": comment, "rating": rating}
        cursor = table.find_one({"_id": show_id})
        
        try:
            if cursor is None:
                table.insert_one({"_id": show_id, "opinion": [opinion]})

            else:
                table.update_one({"_id": show_id}, {"$push": {"opinion": opinion}})
            
            return {'detail': 'ok'}

        except Exception as e:
            print('ERROR DB insert API response onject /show ', e)
            raise HTTPException(status_code=503, detail="DB ERROR conexion no disponible")
    else:
        raise HTTPException(status_code=404, detail="Token invalido o expirado")

#___________________________________ ENTRY POINT ___________________________________
if __name__=='__main__':
    uvicorn.run(app, host='0.0.0.0', port=config('PORT', cast=int))
    client.close()
    sys.exit(0)
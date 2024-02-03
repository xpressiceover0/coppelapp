# db
from pymongo.mongo_client import MongoClient
from decouple import config
from cryptography.fernet import Fernet

fnt=Fernet(bytes(config('key'), encoding='utf-8'))

dbuser=fnt.decrypt(bytes(config('dbuser'), encoding='utf-8')).decode('utf-8')
dbpass=fnt.decrypt(bytes(config('dbpass'), encoding='utf-8')).decode('utf-8')
dburl=config('dburl')

client=None

url = f"mongodb+srv://{dbuser}:{dbpass}@{dburl}/?retryWrites=true&w=majority"
# Create a new client and connect to the server
try:
    client = MongoClient(url)
except Exception as e:
    print('DB no existe o no se logró establecer la conexión', e)

try:
    client.admin.command('ping')
except Exception as e:
    print('DB no responde', e)
    client=None


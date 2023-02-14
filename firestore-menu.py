import firebase_admin
from flask import Flask
from firebase_admin import credentials, firestore, storage
import sqlite3

app = Flask(__name__)

cred = credentials.Certificate('cafe-y-vino-firebase-adminsdk-qdn8s-0f0ac07b32.json')
firebase_admin.initialize_app(cred)
fStore = firestore.client()

db_connection = sqlite3.connect("firestore_manu.sqlite")
cursor = db_connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS platos (
    id TEXT PRIMARY KEY,
    nombre TEXT NON NULL,
    precio TEXT NON NULL,
    descripcion TEXT NON NULL,
    isPresent INTEGER NON NULL,
    imagen BLOB
)
""")

docs = fStore.collection('menu/01.platos/platos').get()
for doc in docs:
    print(doc.get('nombre'))

db_connection.commit()
db_connection.close()
import firebase_admin
from flask import Flask
from firebase_admin import credentials, firestore, storage
import sqlite3
import logging

PLATOS_COLLECTION_PATH = "menu/01.platos/platos"
PIQUEOS_COLLECTION_PATH = "menu/02.piqueos/piqueos"

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

cred = credentials.Certificate('cafe-y-vino-firebase-adminsdk-qdn8s-0f0ac07b32.json')
firebase_admin.initialize_app(cred, {
    "storageBucket": "cafe-y-vino.appspot.com"
})
fStore = firestore.client()
bucket = storage.bucket()

db_connection = sqlite3.connect("firestore_menu.sqlite")
cursor = db_connection.cursor()


def on_snapshot(docs, changes, read_time):
    for change in changes:
        document = change.document
        doc_id = document.id
        doc_data = document.to_dict()
        image_blob = bucket.blob(doc_data["image"])
        doc_image = image_blob.download_as_string()
        if change.type.name == "ADDED":
            cursor.execute(
                "INSERT INTO platos (id, nombre, precio, descripcion, isPresent, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, doc_data["nombre"], doc_data["precio"], doc_data["descripcion"], doc_data["isPresent"],
                 doc_image))
        elif change.type.name == "MODIFIED":
            cursor.execute(
                "UPDATE platos SET nombre=?, precio=?, descripcion=?, isPresent=?, imagen=? WHERE id=?",
                (doc_data["nombre"], doc_data["precio"], doc_data["descripcion"], doc_data["isPresent"],
                 doc_image, doc_id))
        elif change.type.name == "REMOVED":
            cursor.execute("DELETE FROM platos WHERE id=?", (doc_id,))

    db_connection.commit()


def create_table(name):
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {name} (
        id TEXT PRIMARY KEY,
        nombre TEXT NON NULL,
        precio TEXT NON NULL,
        descripcion TEXT NON NULL,
        isPresent INTEGER NON NULL,
        imagen BLOB
    )
    """)


def populate_table(table_name, collection_path):
    collection_snapshot = fStore.collection(collection_path).get()
    for doc_snapshot in collection_snapshot:
        logging.info(f"item's name:: {doc_snapshot.get('nombre')}")
        image_blob = bucket.blob(doc_snapshot.get("image"))
        doc_image = image_blob.download_as_string()
        cursor.execute(f"""
        INSERT INTO {table_name} (id, nombre, precio, descripcion, isPresent, imagen) VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_snapshot.id, doc_snapshot.get("nombre"), doc_snapshot.get("precio"), doc_snapshot.get("descripcion"),
              doc_snapshot.get("isPresent"),
              doc_image))


def listen_collection(collection_path):
    collection_reference = fStore.collection(collection_path)
    collection_watch = collection_reference.on_snapshot(on_snapshot)


create_table("platos")
populate_table("platos", PLATOS_COLLECTION_PATH)
listen_collection(PLATOS_COLLECTION_PATH)


db_connection.close()

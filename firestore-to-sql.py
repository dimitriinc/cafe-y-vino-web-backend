import firebase_admin
from flask import Flask
from firebase_admin import credentials, firestore, storage
import sqlite3
import logging
from collection_table_mapping import Mapping
import datetime

PLATOS_COLLECTION_PATH = "menu/01.platos/platos"
PIQUEOS_COLLECTION_PATH = "menu/02.piqueos/piqueos"
VINOS_BLANCOS_COLLECTION_PATH = "menu/03.vinos/vinos/Vinos blancos/vinos"
VINOS_TINTOS_COLLECTION_PATH = "menu/03.vinos/vinos/Vinos tintos/vinos"
VINOS_ROSE_COLLECTION_PATH = "menu/03.vinos/vinos/Vinos rose/vinos"
VINOS_POSTRE_COLLECTION_PATH = "menu/03.vinos/vinos/Vinos de postre/vinos"
VINOS_COPA_COLLECTION_PATH = "menu/03.vinos/vinos/Vinos por copa/vinos"
COCTELES_COLLECTION_PATH = "menu/04.cocteles/cocteles"
CERVEZAS_COLLECTION_PATH = "menu/05.cervezas/cervezas"
BEBIDAS_CALIENTES_COLLECTION_PATH = "menu/06.bebidas calientes/bebidas calientes"
POSTRES_COLLECTION_PATH = "menu/061.postres/postres"
OFERTAS_COLLECTION_PATH = "menu/07.ofertas/ofertas"

mappings = [
    Mapping(PLATOS_COLLECTION_PATH, "platos"),
    Mapping(PIQUEOS_COLLECTION_PATH, "piqueos"),
    Mapping(VINOS_BLANCOS_COLLECTION_PATH, "vinos_blancos"),
    Mapping(VINOS_TINTOS_COLLECTION_PATH, "vinos_tintos"),
    Mapping(VINOS_ROSE_COLLECTION_PATH, "vinos_rose"),
    Mapping(VINOS_POSTRE_COLLECTION_PATH, "vinos_postre"),
    Mapping(VINOS_COPA_COLLECTION_PATH, "vinos_copa"),
    Mapping(COCTELES_COLLECTION_PATH, "cocteles"),
    Mapping(CERVEZAS_COLLECTION_PATH, "cervezas"),
    Mapping(BEBIDAS_CALIENTES_COLLECTION_PATH, "bebidas_calientes"),
    Mapping(POSTRES_COLLECTION_PATH, "postres"),
    Mapping(OFERTAS_COLLECTION_PATH, "ofertas")
]

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

cred = credentials.Certificate('cafe-y-vino-firebase-adminsdk-qdn8s-0f0ac07b32.json')
firebase_admin.initialize_app(cred, {
    "storageBucket": "cafe-y-vino.appspot.com"
})
fStore = firestore.client()
bucket = storage.bucket()


def custom_on_snapshot(docs, changes, read_time, table_name):
    db_connection = sqlite3.connect("firestore_menu.sqlite")
    cursor = db_connection.cursor()
    for change in changes:
        document = change.document
        doc_id = document.id
        doc_data = document.to_dict()

        image_blob = bucket.blob(doc_data["image"])
        doc_image = image_blob.download_as_string()

        doc_description = "Lo sentimos, este producto no tiene una descripción."
        try:
            doc_description = doc_data["descripcion"]
        except KeyError:
            logging.info(f"{doc_data['nombre']} no tiene una descripcion")

        if change.type.name == "ADDED":
            cursor.execute(
                f"INSERT OR IGNORE INTO {table_name} (id, nombre, precio, descripcion, isPresent, imagen) VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, doc_data["nombre"], doc_data["precio"], doc_description, doc_data["isPresent"],
                 doc_image))
            db_connection.commit()
        elif change.type.name == "MODIFIED":
            logging.info(f"A DOCUMENT IS MODIFIED - {doc_data['nombre']}")
            cursor.execute(
                f"UPDATE {table_name} SET nombre=?, precio=?, descripcion=?, isPresent=?, imagen=? WHERE id=?",
                (doc_data["nombre"], doc_data["precio"], doc_description, doc_data["isPresent"],
                 doc_image, doc_id))
            db_connection.commit()
        elif change.type.name == "REMOVED":
            cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (doc_id,))
            db_connection.commit()


def create_table(name):
    db_connection = sqlite3.connect("firestore_menu.sqlite")
    cursor = db_connection.cursor()
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {name} (
        id TEXT PRIMARY KEY,
        nombre TEXT,
        precio TEXT,
        descripcion TEXT,
        isPresent INTEGER,
        imagen TEXT
    )
    """)
    db_connection.commit()
    db_connection.close()


def populate_table(table_name, collection_path):
    db_connection = sqlite3.connect("firestore_menu.sqlite")
    cursor = db_connection.cursor()
    collection_snapshot = fStore.collection(collection_path).get()
    for doc_snapshot in collection_snapshot:
        logging.info(f"item's name:: {doc_snapshot.get('nombre')}")
        image_blob = bucket.blob(doc_snapshot.get("image"))
        doc_image = image_blob.generate_signed_url(
            method='GET',
            expiration=datetime.datetime(9999, 12, 31)
        )

        doc_description = "Lo sentimos, este producto no tiene una descripción."
        try:
            doc_description = doc_snapshot.get("descripcion")
        except KeyError:
            logging.info(f"{doc_snapshot.get('nombre')} no tiene una descripcion")

        cursor.execute(f"""
        INSERT OR IGNORE INTO {table_name} (id, nombre, precio, descripcion, isPresent, imagen) VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_snapshot.id, doc_snapshot.get("nombre"), doc_snapshot.get("precio"), doc_description,
              doc_snapshot.get("isPresent"),
              doc_image))
        db_connection.commit()
    db_connection.close()


def listen_collection(collection_path, table_name):
    collection_reference = fStore.collection(collection_path)
    collection_watch = collection_reference.on_snapshot(
        lambda docs, changes, read_time: custom_on_snapshot(docs, changes, read_time, table_name)
    )


for mapping in mappings:
    create_table(mapping.get_table_name())
    populate_table(mapping.get_table_name(), mapping.get_collection_path())
    listen_collection(mapping.get_collection_path(), mapping.get_table_name())

if __name__ == '__main__':
    app.run(debug=True, port=8080)

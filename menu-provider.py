from flask import Flask, jsonify, make_response
import sqlite3
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)


def get_collection(table_name):
    connection = sqlite3.connect("firestore_menu.sqlite")
    cursor = connection.cursor()
    collection = cursor.execute(f"SELECT * FROM {table_name} WHERE isPresent=?", (1,))
    connection.close()
    return collection


@app.route('/get-platos')
def get_platos():
    collection = get_collection("platos")


@app.route('/get-piqueos')
def get_piqueos():
    collection = get_collection("piqueos")


@app.route('/get-vinos-blancos')
def get_vinos_blancos():
    collection = get_collection("vinos_blancos")


@app.route('/get-vinos-tintos')
def get_vinos_tintos():
    collection = get_collection("vinos_tintos")


@app.route('/get-vinos-rose')
def get_vinos_rose():
    collection = get_collection("vinos_rose")


@app.route('/get-vinos-postre')
def get_vinos_postre():
    collection = get_collection("vinos_postre")


@app.route('/get-vinos-copa')
def get_vinos_copa():
    collection = get_collection("vinos_copa")


@app.route('/get-cocteles')
def get_cocteles():
    collection = get_collection("cocteles")


@app.route('/get-cervezas')
def get_cervezas():
    collection = get_collection("cervezas")


@app.route('/get-bebidas-calientes')
def get_bebidas_calientes():
    collection = get_collection("bebidas_calientes")


@app.route('/get-postres')
def get_postres():
    collection = get_collection("postres")


@app.route('/get-ofertas')
def get_ofertas():
    collection = get_collection("ofertas")


if __name__ == '__main__':
    app.run(debug=True, port=8080)

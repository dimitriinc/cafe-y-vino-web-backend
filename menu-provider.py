from flask import Flask, jsonify, make_response, request
import sqlite3
import logging
from flask_cors import CORS

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


def get_products(table_name):
    connection = sqlite3.connect("firestore_menu.sqlite")
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {table_name} WHERE isPresent=? ORDER BY nombre", (1,))
    collection = cursor.fetchall()
    cursor.close()
    connection.close()

    results = []

    for product in collection:
        result = {
            'nombre': product[1],
            'precio': product[2],
            'descripcion': product[3],
            'imagen': product[5]
        }
        results.append(result)

    return results


@app.route('/get-collection', methods=['POST'])
def get_collection():
    logging.info("request received")
    table_name = request.args.get('table-name')
    logging.info(f"the table name is:: {table_name}")
    products = get_products(table_name)
    return jsonify(products)


@app.after_request
def after_request(response):
    logging.info("after the request")
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Access-Control-Allow-Origin')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response


if __name__ == '__main__':
    app.run(debug=True, port=8000)

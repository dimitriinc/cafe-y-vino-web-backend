from flask import Flask, request, jsonify, make_response
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import socket
import uuid
import sqlite3
import datetime
from utils import app_specific_password_bot

EMAIL_RECIPIENT = "dimitriinc@proton.me"


# EMAIL_RECIPIENT = "elliotponsic@hotmail.fr"


def validate_email_domain(email):
    domain = email.split('@')[-1]
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False


def create_table():
    db_connection = sqlite3.connect('reservations.sqlite')
    cursor = db_connection.cursor()

    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS reservations (
            id TEXT PRIMARY KEY,
            arrival_timestamp INTEGER,
            name TEXT,
            hour TEXT,
            pax TEXT,
            phone TEXT,
            comment TEXT,
            date TEXT,
            confirmed INTEGER
        )
    """)
    db_connection.commit()
    db_connection.close()


def fetch_reservations_array(date):
    db_connection = sqlite3.connect('reservations.sqlite')
    cursor = db_connection.cursor()
    cursor.execute(f"""
        SELECT * 
        FROM reservations 
        WHERE date=?
        ORDER BY confirmed ASC, arrival_timestamp ASC""", (date,))
    collection = cursor.fetchall()
    cursor.close()
    db_connection.close()

    results = []

    for reservation in collection:
        result = {
            'arrival_timestamp': reservation[1],
            'name': reservation[2],
            'hour': reservation[3],
            'pax': reservation[4],
            'phone': reservation[5],
            'comment': reservation[6],
            'confirmed': reservation[8]
        }
        results.append(result)

    return results


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
logging.basicConfig(level=logging.DEBUG)

cred = credentials.Certificate('cafe-y-vino-firebase-adminsdk-qdn8s-0f0ac07b32.json')
firebase_admin.initialize_app(cred)
fStore = firestore.client()


@app.route('/make-reservation', methods=['POST'])
def make_reservation():
    reservation = request.get_json()
    arrival_timestamp = reservation['arrivalTimestamp']
    name = reservation['name']
    hour = reservation['hour']
    pax = reservation['pax']
    phone = reservation['phone']
    comment = reservation['comment']
    email = reservation['email']
    date = reservation['date']
    doc_id = str(uuid.uuid4())

    logging.info(f"Received a request from {name}. For {pax} persons. On date - {date}")

    if not validate_email_domain(email):
        return make_response("El dominio del email no es válido.", 201)
    else:
        create_table()

        db_connection = sqlite3.connect('reservations.sqlite')
        cursor = db_connection.cursor()
        cursor.execute(f"""
            INSERT INTO reservations (id, arrival_timestamp, name, hour, pax, phone, comment, date, confirmed) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, False)
        """,
                       (doc_id, arrival_timestamp, name, hour, pax, phone, comment, date))
        db_connection.commit()
        db_connection.close()

        msg = MIMEMultipart()

        subject = "Solicitud de reserva"
        html = f'''
            <html><body>
                <div style='padding:2rem;background-color:#fcfaeb;color:#160b17;border:1px solid;border-radius:50px;margin-left:auto;margin-right:auto;margin-bottom:1rem;width:fit-content;'>
                    <p>Nombre:  <em>{name}</em></p>
                    <p>Fecha:  <em>{date}</em></p>
                    <p>Hora:  <em>{hour}</em></p>
                    <p>Pax:  <em>{pax}</em></p>
                    <p>Comentario:  <em>{comment}</em></p>
                    <p>Teléfono:  <em>{phone}</em></p>
                </div>
                <div style='align-text:center'>
                    <a style='text-decoration:none' href="https://d4f3-190-238-135-197.sa.ngrok.io/confirm-reservation?email={email}&name={name}&date={date}&hour={hour}&id={doc_id}"><button style='background-color:#fcfaeb;color:#160b17;padding:1rem;border:1px solid;display:block;margin-bottom:1rem;margin-left:auto;margin-right:auto;border-radius:50px;'>Confirmar</button></a>
                    <a style='text-decoration:none' href="https://d4f3-190-238-135-197.sa.ngrok.io/reject-reservation?email={email}&name={name}&date={date}&hour={hour}&id={doc_id}"><button style='background-color:#fcfaeb;color:#160b17;padding:1rem;border:1px solid;display:block;margin-left:auto;margin-right:auto;border-radius:50px;'>Rechazar</button></a>
                </div>
            </body></html>
        '''

        msg.attach(MIMEText(html, 'html'))
        msg['From'] = "cafeyvinobot@gmail.com"
        msg['To'] = EMAIL_RECIPIENT
        msg['Subject'] = subject

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login("cafeyvinobot@gmail.com", app_specific_password_bot)
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()

        return make_response("La solicitud está enviada!", 200)


@app.route('/get-reservations', methods=['GET', 'POST'])
def get_reservations():
    date = request.args.get('date')
    logging.info(f'DATE REQUEST FOR {date}')
    reservations = fetch_reservations_array(date)
    return jsonify(reservations)


if __name__ == '__main__':
    app.run(debug=True, port=8000)

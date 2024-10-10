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


app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.DEBUG)

cred = credentials.Certificate('cafe-y-vino-firebase-adminsdk-qdn8s-0f0ac07b32.json')
firebase_admin.initialize_app(cred)
fStore = firestore.client()


@app.route('/contact-msg', methods=['POST'])
def receive_msg():
    logging.info("receive-msg has started")

    data = request.get_json()
    name = data.get('name')
    message = data.get('msg')
    email = data.get('email')

    logging.info(f"A contact message received from {name}")

    fStore.collection('mensajes').add({
        "nombre": name,
        "email": email,
        "mensaje": message,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    msg = MIMEMultipart()

    subject = "Un mensaje de contacto"
    html = f'''
    <html><body>
    <p>Enviado por {name}</p>
    <p>Su email: {email}</p>
    <div style='padding:2rem;background-color:#fcfaeb;color:#160b17;border:1px solid;border-radius:50px;margin-right:auto;margin-top:2rem;text-align:start;width:fit-content;'>
    <p>{message}</p>
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
    return jsonify({"message": "Email sent successfully"})


@app.route('/job-application', methods=['POST'])
def apply_job():
    logging.info("apply_job() has started")

    cv_file = request.files['cv']
    name = request.form['name']
    tel = request.form['tel']
    position = request.form['position']
    letter = request.form['letter']

    logging.info(f"cv file's name: {cv_file.filename}")

    cv_file_data = cv_file.read()

    logging.info(f"A job application received from {name} for the position of {position}")

    fStore.collection('aplicaciones_de_trabajo').add({
        "nombre": name,
        "telefono": tel,
        "carta_titular": letter,
        "posicion": position,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

    msg = MIMEMultipart()

    subject = "Solicitud de trabajo"
    html = f'''
    <html><body>
    <p>Enviado por <em>{name}</em></p>
    <p>Su teléfono: <em>{tel}</em></p>
    <p>La posición: <em>{position}</em></p>
    <p style='margin-top:2rem;'>La carta titular:</p>
    <div style='padding:2rem;background-color:#fcfaeb;color:#160b17;border:1px solid;margin-right:auto;text-align:start;margin-left:auto;'>
    <p>{letter}</p>
    </div>
    </body></html>
    '''

    msg.attach(MIMEText(html, 'html'))
    msg['From'] = "cafeyvinobot@gmail.com"
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = subject

    part = MIMEApplication(cv_file_data, Name=cv_file.filename)
    part['Content-Disposition'] = f'attachment; filename="{cv_file.filename}"'
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("cafeyvinobot@gmail.com", app_specific_password_bot)
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    return jsonify({"message": "Email sent successfully"})


@app.route('/signup', methods=['POST'])
def signup():
    logging.info("the signup has started!")

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

    logging.info(f"name: {name}\nemail:{email}")

    if validate_email_domain(email):

        collection_ref = fStore.collection('mailing-list')
        documents = [d for d in collection_ref.where("email", "==", email).stream()]

        if len(documents):
            logging.info("the query is not empty")
            return make_response("Este email ya está en la lista", 201)
        else:
            logging.info("query is EMPTY")
            collection_ref.add({
                "nombre": name,
                "email": email,
                "timestamp": firestore.SERVER_TIMESTAMP
            })
            return make_response("La inscripción exitosa!", 200)

    else:
        return make_response("El dominio del email no es válido.", 201)


if __name__ == '__main__':
    app.run(debug=True, port=8080)

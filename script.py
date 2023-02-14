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


def validate_email_domain(email):
    domain = email.split('@')[-1]
    try:
        socket.gethostbyname(domain)
        return True
    except socket.gaierror:
        return False

# EMAIL_RECIPIENT = "dimitriinc@proton.me"
EMAIL_RECIPIENT = "elliotponsic@hotmail.fr"

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
logging.basicConfig(level=logging.DEBUG)

cred = credentials.Certificate('cafe-y-vino-firebase-adminsdk-qdn8s-0f0ac07b32.json')
firebase_admin.initialize_app(cred)
fStore = firestore.client()

@app.route('/confirm-reservation')
def confirm_reservation():

    name = request.args.get('name')
    date = request.args.get('date')
    hour = request.args.get('hour')
    doc_id = request.args.get('id')

    fStore.document(f"reservas/{date}/reservas/{doc_id}").update({"confirmado": True})

    msg = MIMEMultipart()
    to = request.args.get('email')
    subject = "Confirmación de reserva"
    html = f'''
    <html><body>
    <p>Hola, {name}! Tu reserva para {date} a las {hour} está confirmada.<br>Nos vemos pronto!</p>
    </body></html>
    '''
    msg.attach(MIMEText(html, 'html'))
    msg['From'] = "cafeyvinobot@gmail.com"
    msg['To'] = to
    msg['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("cafeyvinobot@gmail.com", "")
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    return jsonify({"message": "La confirmacion esta enviada exitosamente"})

@app.route('/reject-reservation')
def reject_reservation():

    name = request.args.get('name')
    date = request.args.get('date')
    hour = request.args.get('hour')
    doc_id = request.args.get('id')

    fStore.document(f"reservas/{date}/reservas/{doc_id}").delete()

    msg = MIMEMultipart()
    to = request.args.get('email')
    subject = "Rechazo de reserva"
    html = f'''
    <html><body>
    <p>Hola, {name}! Lo sentimos, pero tu reserva para {date} a las {hour} está rechazada.<br>El restaurante estará en su capasitad a la hora indicada.</p>
    </body></html>
    '''
    msg.attach(MIMEText(html, 'html'))
    msg['From'] = "cafeyvinobot@gmail.com"
    msg['To'] = to
    msg['Subject'] = subject

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("cafeyvinobot@gmail.com", "uvlykbgynynxyxfl")
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    return jsonify({"message": "El rechazo esta enviado exitosamente"})


@app.route('/reservations-request', methods = ['POST'])
def reserv_request():

    data = request.get_json()
    name = data['name']
    tel = data['tel']
    date = data['date']
    hour = data['hour']
    pax = data['pax']
    comment = data['comment']
    email = data['email']

    logging.info(f"Received a request from {name}. The reservation date is {date}.")

    if not validate_email_domain(email):
        return make_response("El dominio del email no es válido.", 201)
    else: 
        doc_ref = fStore.collection(f"reservas/{date}/reservas").add({
            "nombre": name,
            "telefono": tel,
            "hora": hour,
            "pax": pax,
            "comentario": comment,
            "timestamp": firestore.SERVER_TIMESTAMP,
            "confirmado": False
        })

        doc_id = doc_ref[1].id
        logging.info(f"the reservation's ID: {doc_id}")

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
        <p>Teléfono:  <em>{tel}</em></p>
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
        server.login("cafeyvinobot@gmail.com", "")
        server.sendmail(msg['From'], msg['To'], msg.as_string())
        server.quit()
        return make_response("La solicitud está enviada!", 200)
    

    


@app.route('/contact-msg', methods = ['POST'])
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
    server.login("cafeyvinobot@gmail.com", "uvlykbgynynxyxfl")
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    return jsonify({"message": "Email sent successfully"})


@app.route('/job-application', methods = ['POST'])
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

    logging.info("LOG:: we are at the beginnig of the 'part' creation!!!")
    
    part = MIMEApplication(cv_file_data, Name=cv_file.filename)
    part['Content-Disposition'] = f'attachment; filename="{cv_file.filename}"'
    msg.attach(part)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login("cafeyvinobot@gmail.com", "uvlykbgynynxyxfl")
    server.sendmail(msg['From'], msg['To'], msg.as_string())
    server.quit()
    return jsonify({"message": "Email sent successfully"})


@app.route('/signup', methods = ['POST'])
def signup():

    logging.info("the signup() has started!")

    data = request.get_json()
    name = data.get('name')
    email = data.get('email')

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



@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == '__main__':
    app.run(debug = True, port = 8000)


    

import io
import sqlite3
from PIL import Image

conn = sqlite3.connect('firestore_menu.sqlite')
cursor = conn.cursor()
cursor.execute('SELECT imagen FROM platos WHERE nombre=?', ('Canelones de la casa',))
image_data = cursor.fetchone()[0]
image = Image.open(io.BytesIO(image_data))
image.show()

import sqlite3

connection = sqlite3.connect("firestore_menu.sqlite")
cursor = connection.cursor()
cursor.execute(f"SELECT * FROM piqueos WHERE isPresent=? ORDER BY nombre", (1,))
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
    print(result['imagen'])

import mysql.connector
conn = mysql.connector.connect(
    host = "VISHWAK",
    port = 3306,
    user = "root",
    password = "vishwa@12345",
    database = "mydb"
)
if conn.is_connected():
    print("connection sussfully")
else:
    print("connection failed")

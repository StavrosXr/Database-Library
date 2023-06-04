from flask import Flask
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret_key'

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="LibraryDatabase5"
)

mycursor = mydb.cursor()

from routes import *

if __name__ == '__main__':
    app.run(debug=True)

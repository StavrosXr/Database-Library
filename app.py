from flask import Flask
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret_key'

# establish a connection to the MySQL database
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="LibraryDatabase5"
)

# create a cursor object
mycursor = mydb.cursor()

from routes import *


if __name__ == '__main__':
    app.run(debug=True)

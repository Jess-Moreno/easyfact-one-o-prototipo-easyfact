import mysql.connector
from mysql.connector import Error

def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Root",
            database="facturacion_electronica"
        )
    except Error as e:
        print("Error:", e)
        return None

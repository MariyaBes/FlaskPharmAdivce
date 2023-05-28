from flask import Flask, render_template, request, redirect, url_for
import MySQLdb.cursors
from flask_mysqldb import MySQL
import MySQLdb

app = Flask(__name__)
mysql = MySQL(app)

def execute_read_query(connection, query):
    cursor = mysql.connection.cursor()
    result = None
    try:
        cursor.execute(query)
        if cursor.rowcount == 1:
            result = cursor.fetchone()
            result = [result]

        else:
            result = cursor.fetchall()
        return result
    except MySQLdb.OperationalError as e:
        print(f'MySQL server has gone away: {e}, trying to reconnect')
        raise e



def execute_query(connection, query):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute(query)
        cursor.fetchall()
        mysql.connection.commit()

        ID = cursor.lastrowid
        cursor.close()
        return ID
    except MySQLdb.OperationalError as e:
        print(f'MySQL server has gone away: {e}, trying to reconnect')
        raise e
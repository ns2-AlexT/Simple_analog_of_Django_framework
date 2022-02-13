import sqlite3

new_connection = sqlite3.connect('db_local.sqlite')
new_cursor = new_connection.cursor()
with open('data_db.sql', 'r') as f:
    text = f.read()
new_cursor.executescript(text)
new_cursor.close()
new_connection.close()

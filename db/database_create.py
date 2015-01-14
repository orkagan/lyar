import sqlite3, os, sys, os.path
if os.path.isfile('database.db'):
    try:
        os.unlink('database.db')
    except OSError:
        input("Database is already open in another program and cant be changed!Press enter to close.")        
        sys.exit()
conn = sqlite3.connect('database.db')
cur = conn.cursor()
with open('init.sql') as init:
    cur.executescript(init.read())
with open('dummy_data.sql') as data:
    cur.executescript(data.read())
cur.close()
conn.close()

import psycopg2, os
conn = psycopg2.connect(
    dbname="flask_users",
    user="olgaakukina",
    password="",
    host="localhost",
    port="5432"          # тот, что сейчас в коде
)
cur = conn.cursor()
cur.execute("SHOW port;")
print("Port:", cur.fetchone()[0])
cur.execute("SELECT version();")
print(cur.fetchone()[0])

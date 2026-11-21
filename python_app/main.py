from db.conexion import obtener_conexion

con = obtener_conexion()
cur = con.cursor()
cur.execute("SHOW TABLES")
tablas = [t[0] for t in cur.fetchall()]
print(f"Conectado. Tablas encontradas: {len(tablas)}")
print(tablas)
con.close()

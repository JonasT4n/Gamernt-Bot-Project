id, color, type, name FROM uno_raw;""")
    for i in conn.cursor.fetchall():
        print(i)
import psycopg2

password = "gaurav7693"
candidates = [
    ("localhost", 5432),
    ("127.0.0.1", 5432),
    ("gaurav7693", 5432),
    ("localhost", 5433),
]

for host, port in candidates:
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname="postgres",
            user="postgres",
            password=password,
            connect_timeout=3,
        )
        cur = conn.cursor()
        cur.execute("SELECT version()")
        ver = cur.fetchone()[0][:60]
        cur.execute("SELECT datname FROM pg_database ORDER BY 1")
        dbs = [r[0] for r in cur.fetchall()]
        print(f"OK {host}:{port} | {ver}")
        print(f"  databases: {dbs}")
        cur.close()
        conn.close()
    except Exception as exc:
        print(f"FAIL {host}:{port} | {exc}")

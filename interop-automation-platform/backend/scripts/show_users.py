import psycopg2

checks = [
    ("localhost:5432/fhir_validator_db1", dict(host="localhost", port=5432, dbname="fhir_validator_db1", user="postgres", password="gaurav7693")),
    ("127.0.0.1:5432/fhir_validator_db1", dict(host="127.0.0.1", port=5432, dbname="fhir_validator_db1", user="postgres", password="gaurav7693")),
]

for label, kwargs in checks:
    try:
        conn = psycopg2.connect(connect_timeout=3, **kwargs)
        cur = conn.cursor()
        cur.execute("SELECT current_database()")
        print(label, "=>", cur.fetchone()[0])
        cur.execute("SELECT count(*) FROM users")
        print("  count=", cur.fetchone()[0])
        cur.execute("SELECT id, email, full_name FROM users ORDER BY id")
        for row in cur.fetchall():
            print(" ", row)
        cur.close()
        conn.close()
    except Exception as exc:
        print(label, "FAIL", exc)

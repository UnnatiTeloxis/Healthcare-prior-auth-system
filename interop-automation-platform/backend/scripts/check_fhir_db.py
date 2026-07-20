import sys

try:
    import psycopg2
except ImportError:
    print("psycopg2 missing")
    sys.exit(2)

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="fhir_validator_db1",
        user="postgres",
        password="gaurav7693",
    )
    cur = conn.cursor()
    cur.execute("SELECT current_database(), current_user")
    print("connected:", cur.fetchone())
    cur.execute(
        "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1"
    )
    print("tables:", [r[0] for r in cur.fetchall()])
    cur.close()
    conn.close()
except Exception as exc:
    print("FAIL:", type(exc).__name__, exc)
    sys.exit(1)

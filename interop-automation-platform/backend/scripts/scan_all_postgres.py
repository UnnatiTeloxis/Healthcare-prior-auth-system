import socket
import psycopg2

password = "gaurav7693"
ports = [5432, 5433, 5434, 5435, 5436, 5437, 5440]
hosts = ["127.0.0.1", "localhost"]

print("=== scan ===")
for host in hosts:
    for port in ports:
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                dbname="postgres",
                user="postgres",
                password=password,
                connect_timeout=2,
            )
            cur = conn.cursor()
            cur.execute("SHOW server_version")
            ver = cur.fetchone()[0]
            cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false ORDER BY 1")
            dbs = [r[0] for r in cur.fetchall()]
            print(f"OK {host}:{port} PG {ver} dbs={dbs}")
            if "fhir_validator_db1" in dbs:
                cur.close()
                conn.close()
                c2 = psycopg2.connect(
                    host=host,
                    port=port,
                    dbname="fhir_validator_db1",
                    user="postgres",
                    password=password,
                    connect_timeout=2,
                )
                cur2 = c2.cursor()
                cur2.execute("SELECT count(*) FROM users")
                print(f"  fhir_validator_db1.users count={cur2.fetchone()[0]}")
                cur2.execute("SELECT id,email FROM users ORDER BY id")
                for row in cur2.fetchall():
                    print("   ", row)
                cur2.close()
                c2.close()
            else:
                cur.close()
                conn.close()
        except Exception as exc:
            msg = str(exc).split("\n")[0]
            if "password authentication failed" in msg:
                print(f"AUTH_FAIL {host}:{port} ({msg})")
            elif "does not exist" not in msg and "timeout" not in msg.lower():
                # only print meaningful failures briefly
                if "Connection refused" not in msg:
                    print(f"FAIL {host}:{port} {msg[:120]}")

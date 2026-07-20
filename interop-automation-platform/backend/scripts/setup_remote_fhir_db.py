import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

HOST = "192.168.1.251"
PORT = 5432
USER = "postgres"
PASSWORD = "gaurav7693"
DB = "fhir_validator_db1"


def main() -> int:
    try:
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname="postgres",
            user=USER,
            password=PASSWORD,
            connect_timeout=8,
        )
    except Exception as exc:
        print("CONNECT FAIL:", exc)
        return 1

    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SHOW server_version")
    print("version:", cur.fetchone()[0])
    cur.execute("SELECT datname FROM pg_database WHERE datistemplate=false ORDER BY 1")
    dbs = [r[0] for r in cur.fetchall()]
    print("databases:", dbs)

    if DB not in dbs:
        cur.execute(f'CREATE DATABASE "{DB}"')
        print("created", DB)
    else:
        print("database exists:", DB)
    cur.close()
    conn.close()

    conn = psycopg2.connect(
        host=HOST, port=PORT, dbname=DB, user=USER, password=PASSWORD, connect_timeout=8
    )
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL DEFAULT '',
            full_name VARCHAR(255),
            google_id VARCHAR(255) UNIQUE,
            is_verified BOOLEAN DEFAULT FALSE,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT NOW(),
            updated_at TIMESTAMP,
            last_login TIMESTAMP,
            login_count INTEGER DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS ix_users_email ON users (email);

        CREATE TABLE IF NOT EXISTS sessions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token VARCHAR(500) UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT NOW(),
            ip_address VARCHAR(45),
            user_agent TEXT
        );
        CREATE INDEX IF NOT EXISTS ix_sessions_token ON sessions (token);

        CREATE TABLE IF NOT EXISTS validation_history (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            report_id VARCHAR(100) NOT NULL,
            resource_type VARCHAR(50),
            profile_used VARCHAR(255),
            status VARCHAR(20),
            compliance_score INTEGER,
            file_name VARCHAR(255),
            file_size INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
    )
    conn.commit()
    cur.execute("SELECT count(*) FROM users")
    print("users before seed:", cur.fetchone()[0])
    cur.close()
    conn.close()
    print("OK remote ready")
    return 0


if __name__ == "__main__":
    sys.exit(main())

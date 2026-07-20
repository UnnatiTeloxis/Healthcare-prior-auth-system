import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

password = "gaurav7693"
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="postgres",
    user="postgres",
    password=password,
)
conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()
cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("fhir_validator_db1",))
exists = cur.fetchone() is not None
if exists:
    print("database fhir_validator_db1 already exists")
else:
    cur.execute("CREATE DATABASE fhir_validator_db1")
    print("created database fhir_validator_db1")
cur.close()
conn.close()

# Ensure required tables exist (match app models)
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="fhir_validator_db1",
    user="postgres",
    password=password,
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
    CREATE INDEX IF NOT EXISTS ix_users_id ON users (id);

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
    CREATE INDEX IF NOT EXISTS ix_sessions_id ON sessions (id);

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
    CREATE INDEX IF NOT EXISTS ix_validation_history_id ON validation_history (id);
    """
)
conn.commit()
cur.execute(
    "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY 1"
)
print("tables:", [r[0] for r in cur.fetchall()])
cur.close()
conn.close()
print("OK")

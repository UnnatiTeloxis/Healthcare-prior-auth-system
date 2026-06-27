from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = "postgresql://interop:interop123@postgres:5432/interop"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://redis:6379"
    REDIS_CACHE_TTL: int = 3600

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DEBUG: bool = True
    API_RELOAD: bool = True

    # FHIR
    FHIR_SERVER_URL: str = "http://localhost:8080"
    FHIR_SERVER_TIMEOUT: int = 30
    FHIR_SERVER_RETRIES: int = 3
    INFERNO_VALIDATOR_URL: str = "http://fhir-validator-wrapper:4567"
    DEFAULT_IGS: str = "hl7.fhir.us.core#6.1.0"
    CORS_ORIGINS: str = "*"

    # Terminology Server
    TERMINOLOGY_SERVER_URL: str = "https://tx.fhir.org/r4"
    TERMINOLOGY_SERVER_TIMEOUT: int = 30
    TERMINOLOGY_CACHE_TTL: int = 86400

    # CQL
    CQL_CACHE_ENABLED: bool = True
    CQL_CACHE_TTL: int = 3600
    CQL_EXECUTION_TIMEOUT: int = 60

    # Paths
    PROFILES_PATH: str = "/app/data/profiles"
    QUESTIONNAIRES_PATH: str = "/app/data/questionnaires"
    CQL_LIBRARIES_PATH: str = "/app/data/cql_libraries"
    VALUE_SETS_PATH: str = "/app/data/value_sets"
    CRD_SCENARIOS_PATH: str = "/app/data/scenarios/crd"
    VALIDATION_RULES_PATH: str = "/app/data/validation_rules"

    # Security
    AUTH_SECRET_KEY: str = Field(default="change-me-to-a-long-random-secret")
    AUTH_ALGORITHM: str = "HS256"
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60

    @property
    def SECRET_KEY(self) -> str:
        return self.AUTH_SECRET_KEY

    @property
    def ALGORITHM(self) -> str:
        return self.AUTH_ALGORITHM

    @property
    def ACCESS_TOKEN_EXPIRE_MINUTES(self) -> int:
        return self.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES

    @property
    def inferno_validator_url(self) -> str:
        return self.INFERNO_VALIDATOR_URL

    @property
    def default_igs_list(self) -> list[str]:
        return [ig.strip() for ig in self.DEFAULT_IGS.split(",") if ig.strip()]

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    inferno_validator_url: str = "http://fhir-validator-wrapper:4567"
    default_igs: str = "hl7.fhir.us.core#6.1.0"
    cors_origins: str = "*"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def default_igs_list(self) -> List[str]:
        return [ig.strip() for ig in self.default_igs.split(",") if ig.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

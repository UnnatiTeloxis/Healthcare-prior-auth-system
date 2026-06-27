# Interop Automation Platform

Healthcare interoperability testing platform with FHIR Validator, CRD Simulator, and DTR Simulator.

## Structure

- **backend/** - FastAPI application and services
- **frontend/** - React + Vite web application
- **data/** - FHIR profiles, questionnaires, CQL libraries, scenarios, and validation rules
- **docs/** - Architecture and API documentation
- **scripts/** - Setup, seed, test, and deploy scripts

## Getting Started

1. Copy `.env.example` to `.env`
2. Run `make setup` or `scripts/setup.sh`
3. Start with `docker-compose up`

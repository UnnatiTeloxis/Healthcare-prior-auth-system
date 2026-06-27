# FHIR Validator Implementation

A comprehensive FHIR resource validation platform using the Inferno validator wrapper with a Python/FastAPI backend and React/TypeScript frontend.

## Overview

This application validates FHIR (Fast Healthcare Interoperability Resources) payloads against Implementation Guide (IG) profiles. It provides a user-friendly interface for validating FHIR resources and viewing detailed validation results.

## Features

### Core Validation Capabilities
- ✅ **FHIR Structure Validation** - Validates JSON/XML structure and syntax
- ✅ **Profile Validation** - Validates against specific FHIR profiles
- ✅ **Required Fields** - Checks all required fields are present
- ✅ **Cardinality Validation** - Ensures min/max element counts
- ✅ **Data Type Validation** - Validates FHIR data types
- ✅ **Extension Validation** - Validates custom extensions
- ✅ **Standard Rules** - Applies FHIRPath constraints and invariants

### User Interface Features
- 📝 JSON/XML resource editor with file upload
- 🎯 Profile selection by Implementation Guide
- 📊 Detailed validation results with severity categorization
- 📜 Validation history tracking
- 🔄 Re-run past validations

## Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Port 80)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  FastAPI Backend│
│   (Port 8000)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Inferno Wrapper │
│   (Port 4567)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ HL7 FHIR        │
│ Validator       │
└─────────────────┘
```

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.11+ (for local development)

## Quick Start

### Using Docker Compose (Recommended)

1. **Navigate to the project directory:**
```bash
cd Healthcare-prior-auth-system/interop-automation-platform
```

2. **Start all services:**
```bash
docker-compose up -d
```

3. **Access the application:**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Inferno Validator: http://localhost:4567

4. **Stop services:**
```bash
docker-compose down
```

## Pre-loaded Implementation Guides

The following IGs are automatically loaded on startup:
- **US Core** v6.1.0 - Base US healthcare profiles
- **Da Vinci PAS** v2.0.1 - Prior Authorization Support
- **Da Vinci CRD** v2.0.1 - Coverage Requirements Discovery
- **Da Vinci DTR** v2.0.1 - Documentation Templates and Rules
- **CARIN Blue Button** v2.0.0 - Consumer health data access

## Development

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --port 8000
```

Environment variables:
- `INFERNO_VALIDATOR_URL` - Inferno service URL (default: http://fhir-validator-wrapper:4567)
- `DEFAULT_IGS` - Comma-separated list of IGs to load on startup
- `CORS_ORIGINS` - Allowed CORS origins

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Environment variables:
- `VITE_API_BASE_URL` - Backend API URL (default: http://localhost:8000)

## API Endpoints

### Validation Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/validate/` | POST | Validate a single FHIR resource |
| `/api/v1/validate/batch` | POST | Validate multiple resources |
| `/api/v1/validate/profiles` | GET | List available profiles |
| `/api/v1/validate/profiles/by-ig` | GET | Get profiles grouped by IG |

### Implementation Guide Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/igs/` | GET | List loaded IGs |
| `/api/v1/igs/{package_id}` | PUT | Load IG by NPM package ID |
| `/api/v1/igs/upload` | POST | Upload custom IG package.tgz |
| `/api/v1/igs/version` | GET | Get validator version info |

## Usage Examples

### Validate a Patient Resource

1. Navigate to http://localhost/fhir-validator
2. Paste a FHIR Patient resource in JSON format:
```json
{
  "resourceType": "Patient",
  "id": "example",
  "name": [{
    "use": "official",
    "family": "Doe",
    "given": ["John"]
  }],
  "gender": "male",
  "birthDate": "1974-12-25"
}
```
3. Select profiles (optional) - e.g., "US Core Patient Profile"
4. Click "Validate Resource"
5. View validation results with errors, warnings, and information

### Using the API Directly

```bash
# Validate a resource
curl -X POST http://localhost:8000/api/v1/validate/ \
  -H "Content-Type: application/json" \
  -d '{
    "resource": "{\"resourceType\":\"Patient\",\"id\":\"example\"}",
    "profiles": ["http://hl7.org/fhir/us/core/StructureDefinition/us-core-patient"]
  }'

# List available profiles
curl http://localhost:8000/api/v1/validate/profiles

# Load a new IG
curl -X PUT "http://localhost:8000/api/v1/igs/hl7.fhir.us.core?version=6.1.0"
```

## Troubleshooting

### Inferno Service Won't Start
- Check if port 4567 is available
- Increase Docker memory allocation (at least 4GB recommended)
- Check logs: `docker-compose logs fhir-validator-wrapper`

### Validation Takes Too Long
- Disable terminology validation by setting `DISABLE_TX=true` in docker-compose.yml
- Consider using a local terminology server

### Frontend Can't Connect to Backend
- Verify backend is running: `docker-compose ps`
- Check backend logs: `docker-compose logs backend`
- Ensure CORS settings allow frontend origin

## Project Structure

```
interop-automation-platform/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── routers/             # API routes
│   │   ├── services/            # Business logic
│   │   ├── models/              # Pydantic models
│   │   └── utils/               # Utilities
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── fhir_validator/  # Validator components
│   │   ├── services/api/        # API clients
│   │   ├── store/               # Redux state
│   │   ├── types/               # TypeScript types
│   │   └── pages/               # Page components
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Check the documentation
- Review API documentation at http://localhost:8000/docs
- Check Inferno documentation at https://inferno-framework.github.io

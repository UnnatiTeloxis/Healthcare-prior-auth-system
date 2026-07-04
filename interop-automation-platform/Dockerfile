# All-in-one production image for Render.com:
#   - Inferno FHIR validator wrapper (localhost:4567)
#   - FastAPI backend + React frontend (PORT)
#
# Build: docker build -t interop-platform .
# Run:   docker run -p 8000:8000 -e PORT=8000 interop-platform

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --legacy-peer-deps

COPY frontend/ .
RUN npm run build

# Stage 2: Inferno validator (Java wrapper)
FROM infernocommunity/fhir-validator-service:latest AS inferno

# Stage 2b: Bind Inferno to 127.0.0.1 so Render only exposes FastAPI on PORT
FROM inferno AS inferno-launcher-build
COPY scripts/InfernoLocalLauncher.java /build/
RUN /usr/local/openjdk-11/bin/javac -cp '/home/lib/*' -d /build/out /build/InfernoLocalLauncher.java

# Stage 2c: Pre-warm FHIR package cache during build (avoids 503 on cold start)
FROM inferno AS inferno-warm
COPY --from=inferno-launcher-build /build/out /app/inferno-launcher
COPY backend/fhir_packages /app/fhir_packages
COPY scripts/preload-igs.sh /preload-igs.sh
COPY scripts/warm-inferno.sh /warm-inferno.sh
RUN sed -i 's/\r$//' /preload-igs.sh /warm-inferno.sh && \
    chmod +x /preload-igs.sh /warm-inferno.sh && \
    /warm-inferno.sh

# Stage 3: Python app + bundled Inferno
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    FHIR_PACKAGES_PATH=/app/fhir_packages \
    JAVA_HOME=/usr/local/openjdk-11 \
    INFERNO_VALIDATOR_URL=http://127.0.0.1:4567 \
    DISABLE_TX=true \
    DISPLAY_ISSUES_ARE_WARNINGS=true \
    API_RELOAD=false

ENV PATH="${JAVA_HOME}/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Inferno wrapper runtime (Java + service files)
COPY --from=inferno /usr/local/openjdk-11 /usr/local/openjdk-11
COPY --from=inferno /home /home
COPY --from=inferno-launcher-build /build/out /app/inferno-launcher
COPY --from=inferno-warm /root/.fhir /root/.fhir
# Auto-load US Core at Inferno startup (fast path). Other IGs load on demand from /app/fhir_packages.
COPY backend/fhir_packages/us-core.tgz /home/igs/us-core.tgz

COPY backend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY backend/ /app/
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
COPY scripts/start-all.sh /start-all.sh
COPY scripts/preload-igs.sh /preload-igs.sh
RUN sed -i 's/\r$//' /start-all.sh /preload-igs.sh && chmod +x /start-all.sh /preload-igs.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=300s --retries=5 \
    CMD curl -f "http://localhost:${PORT:-8000}/health" || exit 1

CMD ["/start-all.sh"]

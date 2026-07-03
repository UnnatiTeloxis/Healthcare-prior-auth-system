#!/bin/bash
# Push and prepare Render Blueprint deploy.
# Usage: ./scripts/deploy-render.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Preparing Render.com deployment..."

if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "Not inside a git repository."
    exit 1
fi

BRANCH="${DEPLOY_BRANCH:-interop-automation}"

if [[ -n $(git status -s) ]]; then
    echo "Committing changes..."
    git add Dockerfile render.yaml .env.production .dockerignore \
        backend/fhir_packages backend/app/services/fhir_validator/fhir_loader.py \
        docs/DEPLOYMENT_RENDER.md README.md scripts/deploy-render.sh scripts/deploy-render.ps1 \
        ../render.yaml 2>/dev/null || true
    git commit -m "Configure Render single-URL deployment" || true
fi

echo "Pushing to origin/$BRANCH..."
git push origin "$BRANCH"

echo ""
echo "Next: https://dashboard.render.com → New + → Blueprint"
echo "  URL: https://interop-platform.onrender.com"
echo "  Validator: https://interop-platform.onrender.com/fhir-validator.html"

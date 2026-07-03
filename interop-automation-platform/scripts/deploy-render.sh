#!/bin/bash
# Push deployment configuration to GitHub and trigger Render Blueprint deploy.
# Does not modify application source code — only commits deployment files if changed.
#
# Usage (from interop-automation-platform/):
#   chmod +x scripts/deploy-render.sh
#   ./scripts/deploy-render.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "Starting Render.com deployment prep..."

if ! git rev-parse --is-inside-work-tree &> /dev/null; then
    echo "Not inside a git repository. Initialize git and connect GitHub first."
    exit 1
fi

if ! git remote get-url origin &> /dev/null; then
    echo "No GitHub remote 'origin' configured."
    exit 1
fi

BRANCH="${DEPLOY_BRANCH:-main}"

if [[ -n $(git status -s) ]]; then
    echo "Committing deployment configuration..."
    git add render.yaml backend/Dockerfile.render backend/render.yaml \
        frontend/Dockerfile.render frontend/nginx.render.conf \
        docker-compose.render.yml .env.production .dockerignore \
        scripts/deploy-render.sh scripts/deploy-render.ps1 \
        docs/DEPLOYMENT_RENDER.md README.md 2>/dev/null || true
    git commit -m "Add Render.com deployment configuration" || true
fi

echo "Pushing to GitHub (branch: $BRANCH)..."
git push origin "$BRANCH"

echo ""
echo "Deployment push complete."
echo "Next steps:"
echo "  1. Open https://dashboard.render.com"
echo "  2. New + → Blueprint → connect your repository"
echo "  3. Select render.yaml (repo root or interop-automation-platform/)"
echo "  4. Set INFERNO_VALIDATOR_URL in the backend service environment"
echo "  5. Apply and wait 5–10 minutes"
echo ""
echo "Expected URLs:"
echo "  Backend:  https://fhir-validator-backend.onrender.com"
echo "  Frontend: https://fhir-validator-frontend.onrender.com"
echo "  Health:   https://fhir-validator-backend.onrender.com/health"

#!/bin/bash
# Push Docker images to GitHub Container Registry (GHCR)
#
# Authenticates with GHCR using CR_PAT token and pushes both
# Bulletproof Green and Purple agent images with :latest tag.
#
# Prerequisites:
#   - CR_PAT environment variable must be set with a GitHub Personal Access Token
#   - Images must be built first (run scripts/build.sh)
#
# Usage:
#   export CR_PAT=<your-github-pat>
#   export GITHUB_USERNAME=<your-github-username>
#   bash scripts/push.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "Pushing Docker Images to GHCR"
echo "=============================="
echo ""

# Validate required environment variables
GITHUB_USERNAME="${GITHUB_USERNAME:-}"
CR_PAT="${CR_PAT:-}"

if [ -z "$GITHUB_USERNAME" ]; then
  echo -e "${RED}Error: GITHUB_USERNAME environment variable is not set${NC}"
  echo ""
  echo "Usage:"
  echo "  export GITHUB_USERNAME=<your-github-username>"
  echo "  export CR_PAT=<your-github-pat>"
  echo "  bash scripts/push.sh"
  echo ""
  exit 1
fi

if [ -z "$CR_PAT" ]; then
  echo -e "${RED}Error: CR_PAT environment variable is not set${NC}"
  echo ""
  echo "The CR_PAT token is required for GHCR authentication."
  echo ""
  echo "To create a Personal Access Token (PAT):"
  echo "  1. Go to https://github.com/settings/tokens"
  echo "  2. Click 'Generate new token (classic)'"
  echo "  3. Select scopes: write:packages, read:packages, delete:packages"
  echo "  4. Copy the generated token"
  echo ""
  echo "Usage:"
  echo "  export GITHUB_USERNAME=<your-github-username>"
  echo "  export CR_PAT=<your-github-pat>"
  echo "  bash scripts/push.sh"
  echo ""
  exit 1
fi

echo -e "${BLUE}GitHub username:${NC} $GITHUB_USERNAME"
echo -e "${BLUE}Registry:${NC} ghcr.io"
echo ""

# Authenticate with GHCR
echo -e "${GREEN}[1/3] Authenticating with GitHub Container Registry...${NC}"
echo "$CR_PAT" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin

echo -e "${GREEN}✓ Authentication successful${NC}"
echo ""

# Push Green Agent
echo -e "${GREEN}[2/3] Pushing Bulletproof Green Agent...${NC}"
docker push ghcr.io/${GITHUB_USERNAME}/bulletproof-green:latest

echo -e "${GREEN}✓ Green agent pushed successfully${NC}"
echo ""

# Push Purple Agent
echo -e "${GREEN}[3/3] Pushing Bulletproof Purple Agent...${NC}"
docker push ghcr.io/${GITHUB_USERNAME}/bulletproof-purple:latest

echo -e "${GREEN}✓ Purple agent pushed successfully${NC}"
echo ""

# Display summary
echo -e "${GREEN}Push Complete!${NC}"
echo ""
echo "Images pushed to GHCR:"
echo "  - ghcr.io/${GITHUB_USERNAME}/bulletproof-green:latest"
echo "  - ghcr.io/${GITHUB_USERNAME}/bulletproof-purple:latest"
echo ""
echo "View your packages at:"
echo "  https://github.com/${GITHUB_USERNAME}?tab=packages"
echo ""
echo "To use these images, update scenario.toml with:"
echo "  ghcr_url = \"ghcr.io/${GITHUB_USERNAME}/bulletproof-green:latest\""
echo ""

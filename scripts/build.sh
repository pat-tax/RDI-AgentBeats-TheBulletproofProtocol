#!/bin/bash
# Build Docker images for GHCR deployment
#
# Builds both Bulletproof Green and Purple agents for linux/amd64 platform.
# Images are tagged locally and ready for push to GitHub Container Registry.

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "Building Docker Images for GHCR"
echo "==============================="
echo ""

# Get the GitHub username for image naming
GITHUB_USERNAME="${GITHUB_USERNAME:-}"

if [ -z "$GITHUB_USERNAME" ]; then
  echo "GITHUB_USERNAME not set, using 'local' as default"
  GITHUB_USERNAME="local"
fi

echo -e "${BLUE}Building for platform:${NC} linux/amd64"
echo -e "${BLUE}GitHub username:${NC} $GITHUB_USERNAME"
echo ""

# Build Green Agent
echo -e "${GREEN}[1/2] Building Bulletproof Green Agent...${NC}"
docker build \
  --platform linux/amd64 \
  -f Dockerfile.green \
  -t ghcr.io/${GITHUB_USERNAME}/bulletproof-green:latest \
  .

echo -e "${GREEN}✓ Green agent built successfully${NC}"
echo ""

# Build Purple Agent
echo -e "${GREEN}[2/2] Building Bulletproof Purple Agent...${NC}"
docker build \
  --platform linux/amd64 \
  -f Dockerfile.purple \
  -t ghcr.io/${GITHUB_USERNAME}/bulletproof-purple:latest \
  .

echo -e "${GREEN}✓ Purple agent built successfully${NC}"
echo ""

# Display summary
echo -e "${GREEN}Build Complete!${NC}"
echo ""
echo "Images built:"
echo "  - ghcr.io/${GITHUB_USERNAME}/bulletproof-green:latest"
echo "  - ghcr.io/${GITHUB_USERNAME}/bulletproof-purple:latest"
echo ""
echo "Next step: Run scripts/push.sh to push images to GHCR"
echo ""

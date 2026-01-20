#!/bin/bash
# create-release.sh - Create a new release for motion-in-ocean
# This script helps tag and prepare a release

set -e

VERSION_FILE="VERSION"
CHANGELOG_FILE="CHANGELOG.md"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 motion-in-ocean Release Creator${NC}"
echo "======================================"
echo ""

# Check if VERSION file exists
if [ ! -f "${VERSION_FILE}" ]; then
    echo -e "${RED}❌ VERSION file not found${NC}"
    exit 1
fi

# Read current version
CURRENT_VERSION=$(cat "${VERSION_FILE}")
echo -e "Current version: ${GREEN}${CURRENT_VERSION}${NC}"
echo ""

# Ask for new version
echo -e "${YELLOW}Enter new version (e.g., 1.0.1, 1.1.0, 2.0.0):${NC}"
read -r NEW_VERSION

# Validate version format (basic semver check)
if ! [[ "${NEW_VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}❌ Invalid version format. Use semantic versioning (e.g., 1.0.0)${NC}"
    exit 1
fi

echo ""
echo -e "New version will be: ${GREEN}v${NEW_VERSION}${NC}"
echo ""

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo -e "${YELLOW}⚠️  You have uncommitted changes.${NC}"
    echo "Please commit or stash them before creating a release."
    echo ""
    git status --short
    echo ""
    echo -e "${YELLOW}Do you want to continue anyway? (y/N):${NC}"
    read -r CONTINUE
    if [[ ! "${CONTINUE}" =~ ^[Yy]$ ]]; then
        echo "Release cancelled."
        exit 0
    fi
fi

# Update VERSION file
echo "${NEW_VERSION}" > "${VERSION_FILE}"
echo -e "${GREEN}✓${NC} Updated ${VERSION_FILE}"

# Update CHANGELOG (add placeholder for manual editing)
TODAY=$(date +%Y-%m-%d)
CHANGELOG_ENTRY="## [${NEW_VERSION}] - ${TODAY}"

if grep -q "## \[Unreleased\]" "${CHANGELOG_FILE}"; then
    # Add new version entry after [Unreleased] section
    sed -i "/## \[Unreleased\]/a\\
\\
${CHANGELOG_ENTRY}\\
\\
### Changed\\
- Release version ${NEW_VERSION}\\
" "${CHANGELOG_FILE}"
    echo -e "${GREEN}✓${NC} Updated ${CHANGELOG_FILE}"
else
    echo -e "${YELLOW}⚠️  Could not auto-update CHANGELOG. Please update manually.${NC}"
fi

echo ""
echo -e "${BLUE}📝 Release Summary:${NC}"
echo "-----------------------------------"
echo -e "Version: ${GREEN}v${NEW_VERSION}${NC}"
echo -e "Date: ${TODAY}"
echo ""

# Show what will be committed
echo -e "${BLUE}Files to commit:${NC}"
git diff --name-only "${VERSION_FILE}" "${CHANGELOG_FILE}" 2>/dev/null || echo "  ${VERSION_FILE}"
echo ""

# Confirm release
echo -e "${YELLOW}Ready to create release v${NEW_VERSION}? This will:${NC}"
echo "  1. Commit VERSION and CHANGELOG updates"
echo "  2. Create and push git tag v${NEW_VERSION}"
echo "  3. Trigger GitHub Actions to build and publish Docker image"
echo ""
echo -e "${YELLOW}Continue? (y/N):${NC}"
read -r CONFIRM

if [[ ! "${CONFIRM}" =~ ^[Yy]$ ]]; then
    echo "Release cancelled."
    # Restore VERSION file
    echo "${CURRENT_VERSION}" > "${VERSION_FILE}"
    exit 0
fi

# Commit changes
echo ""
echo -e "${BLUE}Committing changes...${NC}"
git add "${VERSION_FILE}" "${CHANGELOG_FILE}"
git commit -m "Release v${NEW_VERSION}"
echo -e "${GREEN}✓${NC} Changes committed"

# Create tag
echo -e "${BLUE}Creating tag v${NEW_VERSION}...${NC}"
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"
echo -e "${GREEN}✓${NC} Tag created"

# Push changes and tag
echo -e "${BLUE}Pushing to remote...${NC}"
git push origin main
git push origin "v${NEW_VERSION}"
echo -e "${GREEN}✓${NC} Pushed to remote"

echo ""
echo -e "${GREEN}✅ Release v${NEW_VERSION} created successfully!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. GitHub Actions will build and publish the Docker image"
echo "  2. Monitor the workflow: https://github.com/hyzhak/pi-camera-in-docker/actions"
echo "  3. Create GitHub release notes: https://github.com/hyzhak/pi-camera-in-docker/releases/new?tag=v${NEW_VERSION}"
echo ""
echo -e "${BLUE}Docker image will be available at:${NC}"
echo "  ghcr.io/hyzhak/pi-camera-in-docker:${NEW_VERSION}"
echo "  ghcr.io/hyzhak/pi-camera-in-docker:latest"
echo ""

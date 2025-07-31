#!/bin/bash
# ==============================================================================
# PEL Project Initializer (pel-init.sh)
#
# This script scaffolds a new project directory from a specified template.
# It copies the template's governance files (Makefile, DOMAIN_BLUEPRINT) and
# creates the necessary directory structure.
#
# Usage: ./scripts/pel-init.sh <template_name> <new_project_name>
# Example: ./scripts/pel-init.sh domain_coding_generic my_new_app
# ==============================================================================

# --- Configuration & Colors ---
set -e # Exit immediately if a command exits with a non-zero status.
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# --- Input Validation ---
if [ "$#" -ne 2 ]; then
    echo -e "${YELLOW}Usage: $0 <template_name> <new_project_name>${NC}"
    echo "Example: $0 domain_coding_generic my_new_app"
    exit 1
fi

TEMPLATE_NAME=$1
PROJECT_NAME=$2
TEMPLATE_DIR="templates/${TEMPLATE_NAME}"
PROJECT_DIR="projects/${PROJECT_NAME}"

if [ ! -d "$TEMPLATE_DIR" ]; then
    echo -e "${YELLOW}Error: Template '${TEMPLATE_NAME}' not found at '${TEMPLATE_DIR}'.${NC}"
    exit 1
fi

if [ -d "$PROJECT_DIR" ]; then
    echo -e "${YELLOW}Error: Project directory '${PROJECT_DIR}' already exists.${NC}"
    exit 1
fi

# --- Scaffolding Logic ---
echo -e "Initializing new project '${PROJECT_NAME}' from template '${TEMPLATE_NAME}'..."

# 1. Create project root directory
mkdir -p "${PROJECT_DIR}"
echo -e "  ${GREEN}✓${NC} Created project directory: ${PROJECT_DIR}"

# 2. Copy and rename governance files
cp "${TEMPLATE_DIR}/Makefile.template" "${PROJECT_DIR}/Makefile"
cp "${TEMPLATE_DIR}/DOMAIN_BLUEPRINT.md.template" "${PROJECT_DIR}/DOMAIN_BLUEPRINT.md"
echo -e "  ${GREEN}✓${NC} Copied Makefile and DOMAIN_BLUEPRINT.md"

# 3. Create standard subdirectories for the project
mkdir -p "${PROJECT_DIR}/personas/specialized"
mkdir -p "${PROJECT_DIR}/instances"
mkdir -p "${PROJECT_DIR}/knowledge_base"
mkdir -p "${PROJECT_DIR}/workflows"
echo -e "  ${GREEN}✓${NC} Created standard subdirectories (personas, instances, etc.)"

# 4. Create a metadata file to link project to its template
echo "template: ${TEMPLATE_NAME}" > "${PROJECT_DIR}/.domain_meta"
echo -e "  ${GREEN}✓${NC} Created .domain_meta file to track template inheritance"

echo -e "\n${GREEN}Project '${PROJECT_NAME}' created successfully.${NC}"
echo -e "Next steps:"
echo -e "1. Add your specialized personas to '${PROJECT_DIR}/personas/specialized/'"
echo -e "2. Customize '${PROJECT_DIR}/DOMAIN_BLUEPRINT.md' for your project."
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

# 1. Create project root and subdirectories
mkdir -p "${PROJECT_DIR}/personas/specialized"
mkdir -p "${PROJECT_DIR}/instances/archive"
mkdir -p "${PROJECT_DIR}/knowledge_base"
mkdir -p "${PROJECT_DIR}/workflows"
echo -e "  ${GREEN}✓${NC} Created standard directory structure."

# 2. Generate the new, minimal Makefile
# CORRECTED: Instead of copying a template, we generate the correct stub.
cat > "${PROJECT_DIR}/Makefile" << EOL
# Makefile for the "${PROJECT_NAME}" Project
# This Makefile inherits all its functionality from the common toolkit.

# --- Project-Specific Configuration ---
PROJECT_NAME := ${PROJECT_NAME}

# --- Include Common Logic ---
include ../../scripts/common.mk

# --- Target Declarations ---
.PHONY: help
.DEFAULT_GOAL := help

# --- Unified Help Target ---
help:
	@echo "$(BLUE)================================================================\$(NC)"
	@echo "  Project: \$(PROJECT_NAME)"
	@echo "$(BLUE)================================================================\$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage: make <command> [ARGS...]\$(NC)"
	@echo ""
	@echo "$(GREEN)Available Commands:\$(NC)"
	@echo "  make generate-prompt INSTANCE=<path>    - Assembles a final prompt from an instance file. (Inherited)"
	@echo "  make archive INSTANCE=<name>            - Archives a completed instance with status 'complete'. (Inherited)"
	@echo "  make archive-failed INSTANCE=<name>     - Archives a completed instance with status 'failed'. (Inherited)"
	@echo "  make clean-backups                      - Removes all .bak files from the instances directory. (Inherited)"
	@echo "  make clean                              - Cleans all generated build artifacts for this project. (Inherited)"
	@echo ""
EOL
echo -e "  ${GREEN}✓${NC} Generated minimal, compliant Makefile."

# 3. Copy DOMAIN_BLUEPRINT and create .domain_meta
cp "${TEMPLATE_DIR}/DOMAIN_BLUEPRINT.md.template" "${PROJECT_DIR}/DOMAIN_BLUEPRINT.md"
echo "template: ${TEMPLATE_NAME}" > "${PROJECT_DIR}/.domain_meta"
echo -e "  ${GREEN}✓${NC} Copied DOMAIN_BLUEPRINT.md and created .domain_meta file."

echo -e "\n${GREEN}Project '${PROJECT_NAME}' created successfully.${NC}"
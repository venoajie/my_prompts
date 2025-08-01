# Makefile
# =====================================================================
# PEL Global Makefile
#
# This Makefile provides repository-wide commands for validation and
# system maintenance. Project-specific commands should be run from
# within the project's own directory.
# =====================================================================

# --- Configuration ---
PYTHON_EXEC := $(shell command -v python3 || command -v python)

# ANSI Color codes
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

# --- Target Declarations ---
.PHONY: help validate update-kb

# --- Default Target ---
.DEFAULT_GOAL := help

# --- Core Commands ---
help:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "  Prompt Engineering Library (PEL) - Global Commands"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:${NC}"
	@echo "  make <command>"
	@echo ""
	@echo "$(GREEN)Global Commands:${NC}"
	@echo "  validate    - Validates all active personas in the library against pel.config.yml."
	@echo "  update-kb   - (Future) Updates the knowledge_base_inventory.yml with the latest source code."
	@echo "  generate-manifest - Scans all projects and generates a persona_manifest.yml."
	@echo ""
	@echo "$(YELLOW)For project-specific commands (like generate-prompt), navigate to the project directory and run 'make help':${NC}"
	@echo "  cd projects/<your_project_name>"
	@echo "  make help"
	@echo ""

validate:
	@echo "$(BLUE)--- Validating All Active Personas ---$(NC)"
	@$(PYTHON_EXEC) scripts/validate_personas.py

update-kb:
	@echo "Updating knowledge base inventory..."
	@$(PYTHON_EXEC) scripts/kb_updater.py

	
generate-manifest:
	@$(PYTHON_EXEC) scripts/generate_manifest.py
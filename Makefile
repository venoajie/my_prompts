# Makefile

# =====================================================================
# PEL Root Makefile (Dispatcher)
#
# This Makefile dispatches commands to project-specific Makefiles.
# It also provides global commands for validation and project creation.
#
# Usage:
#   make <command> PROJECT=<project_name> [ARGS...]
#   make validate
#   make new-project TEMPLATE=<template> NAME=<name>
# =====================================================================

# --- Configuration ---
PYTHON_EXEC := $(shell command -v python3 || command -v python)
VALIDATE_SCRIPT = scripts/validate_personas.py
INIT_SCRIPT = scripts/pel-init.sh

# ANSI Color codes
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

# --- Target Declarations ---
.PHONY: help validate new-project clean

.PHONY: update-kb
update-kb:
	@echo "Updating knowledge base inventory..."
	@$(PYTHON_EXEC) scripts/kb_updater.py
	
# --- Default Target ---
.DEFAULT_GOAL := help

# --- Global Commands ---
help:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "  PEL Dispatcher Makefile"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:${NC}"
	@echo "  make <command> PROJECT=<project_name> [ARGS...]"
	@echo "  make validate"
	@echo "  make new-project TEMPLATE=<template_name> NAME=<new_project_name>"
	@echo ""
	@echo "$(YELLOW)Examples:${NC}"
	@echo "  make generate-prompt PROJECT=coding_trader_app INSTANCE=instances/my_task.instance.md"
	@echo "  make new-project TEMPLATE=domain_coding_generic NAME=my_new_api"
	@echo ""
	@echo "$(GREEN)Global Commands:${NC}"
	@echo "  validate          - Validates all personas in the library (/templates and /projects)."
	@echo "  new-project       - Creates a new project from a template."
	@echo ""
	@echo "$(GREEN)Available Projects:${NC}"
	@$(foreach project, $(wildcard projects/*), echo "  - $(notdir $(project))";)
	@echo ""


validate:
	@echo "$(BLUE)--- Validating All Personas ---$(NC)"
	@$(PYTHON_EXEC) $(VALIDATE_SCRIPT)
	@echo "$(GREEN)✓ Validation complete.$(NC)"

new-project:
	@if [ -z "$(TEMPLATE)" ]; then echo "ERROR: TEMPLATE variable is not set."; exit 1; fi
	@if [ -z "$(NAME)" ]; then echo "ERROR: NAME variable is not set."; exit 1; fi
	@echo "$(BLUE)--- Creating new project '$(NAME)' from template '$(TEMPLATE)' ---$(NC)"
	@bash $(INIT_SCRIPT) $(TEMPLATE) $(NAME)

# --- Dispatcher Logic ---
# This is a catch-all rule that forwards any other command to the
# project-specific Makefile.
%:
	@if [ -z "$(PROJECT)" ]; then \
		echo "$(YELLOW)ERROR: You must specify a PROJECT for this command.${NC}"; \
		echo "Usage: make $@ PROJECT=<project_name>"; \
		exit 1; \
	fi
	@if [ ! -d "projects/$(PROJECT)" ]; then \
		echo "$(YELLOW)ERROR: Project '$(PROJECT)' not found in 'projects/'.${NC}"; \
		exit 1; \
	fi
	@echo "$(BLUE)--- Dispatching command '$(@)' to project '$(PROJECT)' ---$(NC)"
	@$(MAKE) -C projects/$(PROJECT) $(@) $(filter-out PROJECT=%,$(MAKECMDGOALS))
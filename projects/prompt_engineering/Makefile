# Makefile for the "$(PROJECT_NAME)" Project
# This Makefile inherits all its functionality from the common toolkit.

# --- Project-Specific Configuration ---
# Set this to the name of the project directory.
PROJECT_NAME := language_learning # <-- CHANGE THIS TO 'prompt_engineering' FOR THE OTHER FILE

# --- Include Common Logic ---
# All functionality is inherited from this central file.
include ../../scripts/common.mk

# --- Target Declarations ---
.PHONY: help
.DEFAULT_GOAL := help

# --- Unified Help Target ---
help:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "  Project: $(PROJECT_NAME)"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage: make <command> [ARGS...]$(NC)"
	@echo ""
	@echo "$(GREEN)Available Commands:$(NC)"
	@echo "  make generate-prompt INSTANCE=<path>    - Assembles a final prompt from an instance file. (Inherited)"
	@echo "  make archive INSTANCE=<name>            - Archives a completed instance with status 'complete'. (Inherited)"
	@echo "  make archive-failed INSTANCE=<name>     - Archives a completed instance with status 'failed'. (Inherited)"
	@echo "  make clean-backups                      - Removes all .bak files from the instances directory. (Inherited)"
	@echo "  make clean                              - Cleans all generated build artifacts for this project. (Inherited)"
	@echo ""
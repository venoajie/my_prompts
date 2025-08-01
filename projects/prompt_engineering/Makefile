# Makefile for the "$(PROJECT_NAME)" Project
# This Makefile inherits all its functionality from the common toolkit.

# --- Project-Specific Configuration ---
PROJECT_NAME := language_learning # or prompt_engineering

# --- Include Common Logic ---
include ../../scripts/common.mk

# --- Target Declarations ---
.PHONY: help
.DEFAULT_GOAL := help

# --- Project-Specific Help ---
help:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "  Project: $(PROJECT_NAME)"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage: make <command> [ARGS...]$(NC)"
	@echo ""
	@$(MAKE) -f ../../scripts/common.mk help-common
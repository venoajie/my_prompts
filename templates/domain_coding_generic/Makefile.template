# =====================================================================
# PEL Project Makefile (Template: domain_coding_generic)
#
# This Makefile provides core commands for a standard coding project.
# It is designed to be customized for specific project needs.
# =====================================================================

# --- Configuration ---
PYTHON_EXEC := $(shell command -v python3 || command -v python)
PEL_TOOLKIT_SCRIPT = ../../scripts/pel_toolkit.py
BUILD_DIR = ../../build/$(shell basename `pwd`) # Project-specific build dir

# ANSI Color codes
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

# --- Target Declarations ---
.PHONY: help generate-prompt clean

# --- Default Target ---
.DEFAULT_GOAL := help

# --- Core Commands ---
help:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "  Project: $(shell basename `pwd`)"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage:${NC}"
	@echo "  make <command> [ARGS...]"
	@echo ""
	@echo "$(GREEN)Core Commands:${NC}"
	@echo "  generate-prompt INSTANCE=<path>   - Assembles a final prompt from an instance file."
	@echo "  clean                           - Cleans all generated build artifacts for this project."
	@echo ""

generate-prompt:
	@if [ -z "$(INSTANCE)" ]; then \
		echo "$(YELLOW)ERROR: INSTANCE variable must be set.${NC}"; \
		echo "Usage: make generate-prompt INSTANCE=instances/your_task.instance.md"; \
		exit 1; \
	fi
	@mkdir -p $(BUILD_DIR)
	@INSTANCE_BASENAME=$$(basename $(INSTANCE) .instance.md); \
	OUTPUT_FILE=$(BUILD_DIR)/$${INSTANCE_BASENAME}.prompt.xml; \
	echo "Generating prompt for [$(INSTANCE)] -> [$${OUTPUT_FILE}]"; \
	$(PYTHON_EXEC) $(PEL_TOOLKIT_SCRIPT) $(INSTANCE) > $${OUTPUT_FILE}; \
	echo "$(GREEN)✓ Prompt generated successfully.${NC}"

clean:
	@echo "Cleaning project-specific build directory: $(BUILD_DIR)"
	@rm -rf $(BUILD_DIR)
# /scripts/common.mk
# Version: 1.0
# This file contains all common, shared logic for project Makefiles.
# It is intended to be included by project-specific Makefiles.

# --- Common Configuration ---
# These variables are expected to be available for all projects.
ROOT_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))/..
PYTHON_EXEC := $(shell command -v python3 || command -v python)
PEL_TOOLKIT_SCRIPT = $(ROOT_DIR)/scripts/pel_toolkit.py
BUILD_DIR = $(ROOT_DIR)/build/$(PROJECT_NAME) # Expects PROJECT_NAME to be set by the calling Makefile

INSTANCE_DIR := instances
ARCHIVE_DIR := $(INSTANCE_DIR)/archive
TODAY := $(shell date +%Y-%m-%d)

# ANSI Color codes for pretty output
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

# --- Common Targets ---
.PHONY: generate-prompt archive archive-failed clean-backups clean

generate-prompt:
	@if [ -z "$(INSTANCE)" ]; then \
		echo "$(YELLOW)ERROR: Please specify the instance file.${NC}"; \
		echo "Usage: make generate-prompt INSTANCE=instances/your_task.instance.md"; \
		exit 1; \
	fi
	@mkdir -p $(BUILD_DIR)
	@INSTANCE_BASENAME=$$(basename $(INSTANCE) .instance.md); \
	OUTPUT_FILE=$(BUILD_DIR)/$${INSTANCE_BASENAME}.prompt.xml; \
	echo "Generating prompt for [$(INSTANCE)] -> [$${OUTPUT_FILE}]"; \
	$(PYTHON_EXEC) $(PEL_TOOLKIT_SCRIPT) $(INSTANCE) > $${OUTPUT_FILE}; \
	echo "$(GREEN)✓ Prompt generated successfully in $(BUILD_DIR)$(NC)"

archive: _check_instance
	@mkdir -p $(ARCHIVE_DIR)
	@mv "$(INSTANCE_DIR)/$(INSTANCE).instance.md" "$(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_complete.instance.md"
	@echo "Archived $(INSTANCE).instance.md to $(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_complete.instance.md"

archive-failed: _check_instance
	@mkdir -p $(ARCHIVE_DIR)
	@mv "$(INSTANCE_DIR)/$(INSTANCE).instance.md" "$(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_failed.instance.md"
	@echo "Archived $(INSTANCE).instance.md as failed to $(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_failed.instance.md"

clean-backups:
	@find $(INSTANCE_DIR) -name "*.bak" -type f -delete
	@echo "Removed all .bak files from $(INSTANCE_DIR)."

clean:
	@echo "Cleaning project-specific build directory: $(BUILD_DIR)"
	@rm -rf $(BUILD_DIR)

# --- Common Helper Targets ---
.PHONY: _check_instance
_check_instance:
	@if [ -z "$(INSTANCE)" ]; then \
		echo "$(YELLOW)Error: INSTANCE variable is not set.${NC}"; \
		echo "Usage: make archive INSTANCE=<instance_name>"; \
		exit 1; \
	fi
	@if [ ! -f "$(INSTANCE_DIR)/$(INSTANCE).instance.md" ]; then \
		echo "$(YELLOW)Error: Instance file '$(INSTANCE_DIR)/$(INSTANCE).instance.md' not found.${NC}"; \
		exit 1; \
	fi
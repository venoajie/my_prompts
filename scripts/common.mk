# /scripts/common.mk
# Version: 3.0 (Defensive & Sanitized)

# --- Special Targets ---
# Ensures the entire recipe runs in a single, predictable shell instance.
.ONESHELL:

# --- Common Configuration ---
# This is the most robust, paranoid, and definitive way to define paths.
# The $(strip ...) function removes any accidental or buggy whitespace.
ROOT_DIR_RAW := $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/..)
ROOT_DIR := $(strip $(ROOT_DIR_RAW))

# Export key variables to ensure they are available in sub-shells.
export ROOT_DIR
export PROJECT_NAME

PYTHON_EXEC := $(shell command -v python3 || command -v python)
PEL_TOOLKIT_SCRIPT = $(ROOT_DIR)/scripts/pel_toolkit.py

# Sanitize the final BUILD_DIR as well for maximum safety.
BUILD_DIR_RAW = $(ROOT_DIR)/build/$(PROJECT_NAME)
BUILD_DIR := $(strip $(BUILD_DIR_RAW))

INSTANCE_DIR := instances
ARCHIVE_DIR := $(INSTANCE_DIR)/archive
TODAY := $(shell date +%Y-%m-%d)

GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

# --- Common Targets ---
.PHONY: generate-prompt archive archive-failed clean-backups clean

generate-prompt:
	@if [ -z "$(INSTANCE)" ]; then
		echo "$(YELLOW)ERROR: Please specify the instance file.${NC}"
		echo "Usage: make generate-prompt INSTANCE=instances/your_task.instance.md"
		exit 1
	fi
	
	@mkdir -p "$(BUILD_DIR)"
	
	# DEFINITIVE FIX: This recipe is now as simple and robust as possible.
	INSTANCE_BASENAME=$$(basename "$(INSTANCE)" .instance.md)
	OUTPUT_FILE="$(BUILD_DIR)/$${INSTANCE_BASENAME}.prompt.xml"
	
	echo "Generating prompt for [$(INSTANCE)] -> [$${OUTPUT_FILE}]"
	$(PYTHON_EXEC) "$(PEL_TOOLKIT_SCRIPT)" "$(INSTANCE)" > "$${OUTPUT_FILE}"
	
	@echo "$(GREEN)✓ Prompt generated successfully in $(BUILD_DIR)$(NC)"

archive:
	@if [ -z "$(INSTANCE)" ]; then exit 1; fi
	@if [ ! -f "$(INSTANCE_DIR)/$(INSTANCE).instance.md" ]; then exit 1; fi
	@mkdir -p "$(ARCHIVE_DIR)"
	@mv "$(INSTANCE_DIR)/$(INSTANCE).instance.md" "$(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_complete.instance.md"
	@echo "Archived $(INSTANCE).instance.md to $(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_complete.instance.md"

archive-failed:
	@if [ -z "$(INSTANCE)" ]; then exit 1; fi
	@if [ ! -f "$(INSTANCE_DIR)/$(INSTANCE).instance.md" ]; then exit 1; fi
	@mkdir -p "$(ARCHIVE_DIR)"
	@mv "$(INSTANCE_DIR)/$(INSTANCE).instance.md" "$(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_failed.instance.md"
	@echo "Archived $(INSTANCE).instance.md as failed to $(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_failed.instance.md"

clean-backups:
	@find "$(INSTANCE_DIR)" -name "*.bak" -type f -delete
	@echo "Removed all .bak files from $(INSTANCE_DIR)."

clean:
	@echo "Cleaning project-specific build directory: $(BUILD_DIR)"
	@rm -rf "$(BUILD_DIR)"
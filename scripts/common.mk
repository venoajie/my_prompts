# /scripts/common.mk
# Version: 3.3 (Final Dynamic Project Name)

# --- Special Targets ---
# Ensures the entire recipe runs in a single, predictable shell instance.
.ONESHELL:

# --- Common Configuration ---
ROOT_DIR := $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/..)

# CORRECTED: This is the most direct and robust method. It dynamically gets
# the base name of the current working directory where 'make' is being run.
PROJECT_NAME := $(shell basename `pwd`)

export ROOT_DIR
export PROJECT_NAME

PYTHON_EXEC := $(shell command -v python3 || command -v python)
PEL_TOOLKIT_SCRIPT = $(ROOT_DIR)/scripts/pel_toolkit.py
BUILD_DIR = $(ROOT_DIR)/build/$(PROJECT_NAME)

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
	
	INSTANCE_BASENAME=$$(basename "$(INSTANCE)" .instance.md)
	OUTPUT_FILE="$(BUILD_DIR)/$${INSTANCE_BASENAME}.prompt.xml"
	
	echo "Generating prompt for [$(INSTANCE)] -> [$${OUTPUT_FILE}]"
	$(PYTHON_EXEC) "$(PEL_TOOLKIT_SCRIPT)" "$(INSTANCE)" > "$${OUTPUT_FILE}" || exit $$?
	
	@echo "$(GREEN)✓ Prompt generated successfully in $(BUILD_DIR)$(NC)"

# ... (rest of the file is unchanged) ...
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
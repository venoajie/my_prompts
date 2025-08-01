# /scripts/common.mk
# Version: 2.0 (ONESHELL Implementation)

# --- Special Targets ---
# This  tells make to run the entire recipe
# in a single shell instance, making it behave like a normal script.
.ONESHELL:

# --- Common Configuration ---
ROOT_DIR := $(realpath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/..)
export ROOT_DIR
export PROJECT_NAME

PYTHON_EXEC := $(shell command -v python3 || command -v python)
PEL_TOOLKIT_SCRIPT = $(ROOT_DIR)/scripts/pel_toolkit.py
BUILD_DIR = $(ROOT_DIR)/build/$(PROJECT_NAME)

INSTANCE_DIR := instances
ARCHIVE_DIR := $(INSTANCE_DIR)/archive
TODAY := $(shell date +%Y-%m-%d)

GREEN = \033[0;32m
YELLOW = \03-3[1;33m
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
	
	@mkdir -p $(BUILD_DIR)
	
	# CORRECTED: This now runs in a single shell. No backslashes are needed.
	# Semicolons are no longer required. Each command is on its own line.
	INSTANCE_BASENAME=$$(basename $(INSTANCE) .instance.md)
	OUTPUT_FILE="$(BUILD_DIR)/$${INSTANCE_BASENAME}.prompt.xml"
	
	echo "Generating prompt for [$(INSTANCE)] -> [$${OUTPUT_FILE}]"
	$(PYTHON_EXEC) $(PEL_TOOLKIT_SCRIPT) $(INSTANCE) > "$${OUTPUT_FILE}"
	
	@echo "$(GREEN)✓ Prompt generated successfully in $(BUILD_DIR)$(NC)"

archive:
	@if [ -z "$(INSTANCE)" ]; then exit 1; fi
	@if [ ! -f "$(INSTANCE_DIR)/$(INSTANCE).instance.md" ]; then exit 1; fi
	@mkdir -p $(ARCHIVE_DIR)
	@mv "$(INSTANCE_DIR)/$(INSTANCE).instance.md" "$(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_complete.instance.md"
	@echo "Archived $(INSTANCE).instance.md to $(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_complete.instance.md"

archive-failed:
	@if [ -z "$(INSTANCE)" ]; then exit 1; fi
	@if [ ! -f "$(INSTANCE_DIR)/$(INSTANCE).instance.md" ]; then exit 1; fi
	@mkdir -p $(ARCHIVE_DIR)
	@mv "$(INSTANCE_DIR)/$(INSTANCE).instance.md" "$(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_failed.instance.md"
	@echo "Archived $(INSTANCE).instance.md as failed to $(ARCHIVE_DIR)/$(TODAY)_$(INSTANCE)_failed.instance.md"

clean-backups:
	@find $(INSTANCE_DIR) -name "*.bak" -type f -delete
	@echo "Removed all .bak files from $(INSTANCE_DIR)."

clean:
	@echo "Cleaning project-specific build directory: $(BUILD_DIR)"
	@rm -rf $(BUILD_DIR)

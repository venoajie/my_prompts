# =====================================================================
# Makefile for the "coding_trader_app" Project
# Version: 2.0 (Project-Specific)
# =====================================================================

# --- Configuration ---
# The path to the global toolkit script is now relative from the project root.
PYTHON_EXEC := $(shell command -v python3 || command -v python)
PEL_TOOLKIT_SCRIPT = ../../scripts/pel_toolkit.py
# The build directory is now located at the root level, in a project-specific subdir
BUILD_DIR = ../../build/coding_trader_app
TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)

# ANSI Color codes for pretty output
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

# --- Target Declarations ---
.PHONY: help generate-prompt end-session generate-manifest-prompt \
        generate-jules-task review-report debug-failed-run clean

# --- Default Target ---
.DEFAULT_GOAL := help

# =====================================================================
# HELP AND DOCUMENTATION
# =====================================================================
help:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "   Project: coding_trader_app - Automation Tool"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage: make [target] [VARIABLE=value]$(NC)"
	@echo ""
	@echo "$(GREEN)Core Workflows:$(NC)"
	@echo "  make generate-prompt INSTANCE=<path>   - Assembles a final prompt XML from an instance file."
	@echo "  make end-session LOG=<path>            - Creates a synthesis prompt from a session log."
	@echo ""
	@echo "$(GREEN)Jules Integration Workflows (Optional):$(NC)"
	@echo "  make generate-manifest-prompt INSTANCE=<path> - Generates a prompt to create a JULES_MANIFEST.json."
	@echo "  make generate-jules-task INSTANCE=<path>      - Generates a guided prompt for a generative Jules task."
	@echo "  make review-report REPORT=<path>       - Generates a prompt to analyze a JULES_REPORT.json."
	@echo "  make debug-failed-run REPORT=<path> SOURCE=<path> - Generates a prompt to debug a failed Jules run."
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make clean                             - Cleans all generated build artifacts for this project."
	@echo ""

# =====================================================================
# CORE WORKFLOWS
# =====================================================================
generate-prompt:
	@if [ -z "$(INSTANCE)" ]; then \
		echo "ERROR: Please specify the instance file."; \
		echo "Usage: make generate-prompt INSTANCE=instances/your_task.instance.md"; \
		exit 1; \
	fi;
	@mkdir -p $(BUILD_DIR);
	@INSTANCE_BASENAME=$$(basename $(INSTANCE) .instance.md); \
	OUTPUT_FILE=$(BUILD_DIR)/$${INSTANCE_BASENAME}.prompt.xml; \
	echo "Generating prompt for [$(INSTANCE)] -> [$${OUTPUT_FILE}]"; \
	$(PYTHON_EXEC) $(PEL_TOOLKIT_SCRIPT) $(INSTANCE) > $${OUTPUT_FILE}; \
	echo "$(GREEN)✓ Prompt generated successfully in $(BUILD_DIR)$(NC)"

end-session:
	@if [ -z "$(LOG)" ]; then \
		echo "ERROR: Please specify the session log file."; \
		exit 1; \
	fi
	@echo "Synthesizing session log: $(LOG)"
	@mkdir -p $(BUILD_DIR);
	@SYNTH_INSTANCE_FILE=$(BUILD_DIR)/synthesize-session-$(TIMESTAMP).instance.md; \
	echo "---" > $${SYNTH_INSTANCE_FILE}; \
	echo "persona_alias: session-synthesizer" >> $${SYNTH_INSTANCE_FILE}; \
	echo "---" >> $${SYNTH_INSTANCE_FILE}; \
	echo "<Mandate><Inject src=\"$(LOG)\" /></Mandate>" >> $${SYNTH_INSTANCE_FILE}; \
	\
	SYNTH_PROMPT_FILE=$(BUILD_DIR)/synthesize-session-$(TIMESTAMP).prompt.xml; \
	$(MAKE) generate-prompt INSTANCE=$${SYNTH_INSTANCE_FILE}; \
	\
	echo ""; \
	echo "$(YELLOW)--------------------------- ACTION REQUIRED ---------------------------$(NC)"; \
	echo "A synthesis prompt has been generated at: $(GREEN)$${SYNTH_PROMPT_FILE}$(NC)"; \
	echo "1. Copy the content of this file and execute it with your LLM."; \
	echo "2. Save the resulting JSON output to your knowledge_base (e.g., session_synthesis_latest.json)."; \
	echo "$(YELLOW)-----------------------------------------------------------------------$(NC)";

# =====================================================================
# JULES INTEGRATION WORKFLOWS
# =====================================================================
generate-manifest-prompt:
	@$(MAKE) generate-prompt INSTANCE=$(INSTANCE)

generate-jules-task:
	@$(MAKE) generate-prompt INSTANCE=$(INSTANCE)

review-report:
	@if [ -z "$(REPORT)" ]; then echo "ERROR: REPORT not set"; exit 1; fi
	@REVIEW_INSTANCE_FILE=$(BUILD_DIR)/review-report.instance.md; \
	echo "---" > $${REVIEW_INSTANCE_FILE}; \
	echo "persona_alias: jri-1" >> $${REVIEW_INSTANCE_FILE}; \
	echo "---" >> $${REVIEW_INSTANCE_FILE}; \
	echo "<Mandate><Inject src=\"$(REPORT)\" /></Mandate>" >> $${REVIEW_INSTANCE_FILE}; \
	$(MAKE) generate-prompt INSTANCE=$${REVIEW_INSTANCE_FILE}

debug-failed-run:
	@if [ -z "$(REPORT)" ]; then echo "ERROR: REPORT not set"; exit 1; fi
	@if [ -z "$(SOURCE)" ]; then echo "ERROR: SOURCE not set"; exit 1; fi
	@DEBUG_INSTANCE_FILE=$(BUILD_DIR)/debug-run.instance.md; \
	echo "---" > $${DEBUG_INSTANCE_FILE}; \
	echo "persona_alias: da-1" >> $${DEBUG_INSTANCE_FILE}; \
	echo "---" >> $${DEBUG_INSTANCE_FILE}; \
	echo "<Mandate>" >> $${DEBUG_INSTANCE_FILE}; \
	echo "  <Inject src=\"$(REPORT)\" />" >> $${DEBUG_INSTANCE_FILE}; \
	echo "  <Inject src=\"$(SOURCE)\" />" >> $${DEBUG_INSTANCE_FILE}; \
	echo "</Mandate>" >> $${DEBUG_INSTANCE_FILE}; \
	$(MAKE) generate-prompt INSTANCE=$${DEBUG_INSTANCE_FILE}

# =====================================================================
# UTILITIES
# =====================================================================
clean:
	@echo "Cleaning project-specific build directory: $(BUILD_DIR)"
	@rm -rf $(BUILD_DIR)
# =====================================================================
# Makefile for the "coding_trader_app" Project
# Version: 2.1 (Refactored for Project-Scoped Context)
# =====================================================================

# --- Configuration ---
# Paths are relative from this project's root directory.
# The global toolkit script is two levels up.
PYTHON_EXEC := $(shell command -v python3 || command -v python)
PEL_TOOLKIT_SCRIPT = ../../scripts/pel_toolkit.py
# The build directory is at the root level, in a project-specific subdir.
BUILD_DIR = ../../build/coding_trader_app
TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)

# ANSI Color codes
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
	@echo "  Project: coding_trader_app - Automation Tool"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage: make [target] [VARIABLE=value]$(NC)"
	@echo "  (Run from root as: make <target> PROJECT=coding_trader_app ...)"
	@echo ""
	@echo "$(GREEN)Core Workflows:$(NC)"
	@echo "  generate-prompt INSTANCE=<path>   - Assembles a final prompt XML from an instance file."
	@echo "  end-session LOG=<path>            - Creates a synthesis prompt from a session log."
	@echo ""
	@echo "$(GREEN)Jules Integration Workflows:$(NC)"
	@echo "  generate-manifest-prompt INSTANCE=<path> - Generates a prompt to create a JULES_MANIFEST.json."
	@echo "  generate-jules-task INSTANCE=<path>      - Generates a guided prompt for a generative Jules task."
	@echo "  review-report REPORT=<path>       - Generates a prompt to analyze a JULES_REPORT.json."
	@echo "  debug-failed-run REPORT=<path> SOURCE=<path> - Generates a prompt to debug a failed Jules run."
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  clean                             - Cleans all generated build artifacts for this project."
	@echo ""

# =====================================================================
# CORE WORKFLOWS
# =====================================================================
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
	echo "$(GREEN)✓ Prompt generated successfully in $(BUILD_DIR)$(NC)"

end-session:
	@if [ -z "$(LOG)" ]; then echo "$(YELLOW)ERROR: LOG variable must be set.${NC}"; exit 1; fi
	@echo "Synthesizing session log: $(LOG)"
	@mkdir -p $(BUILD_DIR)
	@# This workflow creates a temporary instance file to run the synthesizer persona.
	@# Note that the persona_alias does not need a domain, as it's assumed to be in this project.
	@SYNTH_INSTANCE_FILE=$(BUILD_DIR)/synthesize-session-$(TIMESTAMP).instance.md; \
	echo "---" > $${SYNTH_INSTANCE_FILE}; \
	echo "persona_alias: session-synthesizer" >> $${SYNTH_INSTANCE_FILE}; \
	echo "---" >> $${SYNTH_INSTANCE_FILE}; \
	echo "<Mandate><Inject src=\"$(LOG)\" /></Mandate>" >> $${SYNTH_INSTANCE_FILE}; \
	\
	$(MAKE) generate-prompt INSTANCE=$${SYNTH_INSTANCE_FILE}; \
	\
	echo ""; \
	echo "$(YELLOW)--------------------------- ACTION REQUIRED ---------------------------$(NC)"; \
	echo "A synthesis prompt has been generated at: $(GREEN)$(BUILD_DIR)/synthesize-session-$(TIMESTAMP).prompt.xml$(NC)"; \
	echo "1. Copy the content of this file and execute it with your LLM."; \
	echo "2. Save the resulting JSON output to this project's knowledge_base."; \
	echo "$(YELLOW)-----------------------------------------------------------------------$(NC)";

# =====================================================================
# JULES INTEGRATION WORKFLOWS
# =====================================================================
# These targets simply chain to the generic 'generate-prompt' target.
generate-manifest-prompt:
	@$(MAKE) generate-prompt INSTANCE=$(INSTANCE)

generate-jules-task:
	@$(MAKE) generate-prompt INSTANCE=$(INSTANCE)

review-report:
	@if [ -z "$(REPORT)" ]; then echo "$(YELLOW)ERROR: REPORT not set${NC}"; exit 1; fi
	@REVIEW_INSTANCE_FILE=$(BUILD_DIR)/review-report-$(TIMESTAMP).instance.md; \
	echo "---" > $${REVIEW_INSTANCE_FILE}; \
	echo "persona_alias: jri-1" >> $${REVIEW_INSTANCE_FILE}; \
	echo "---" >> $${REVIEW_INSTANCE_FILE}; \
	echo "<Mandate><Inject src=\"$(REPORT)\" /></Mandate>" >> $${REVIEW_INSTANCE_FILE}; \
	$(MAKE) generate-prompt INSTANCE=$${REVIEW_INSTANCE_FILE}

debug-failed-run:
	@if [ -z "$(REPORT)" ]; then echo "$(YELLOW)ERROR: REPORT not set${NC}"; exit 1; fi
	@if [ -z "$(SOURCE)" ]; then echo "$(YELLOW)ERROR: SOURCE not set${NC}"; exit 1; fi
	@DEBUG_INSTANCE_FILE=$(BUILD_DIR)/debug-run-$(TIMESTAMP).instance.md; \
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

	# Add to the .PHONY declaration
.PHONY: analyze-incident

# Add to the help text
@echo "  analyze-incident LOGS=<path>      - Triggers an LLM to analyze incident logs."

analyze-incident:
	@if [ -z "$(LOGS)" ]; then echo "ERROR: LOGS variable must be set to a log file or directory."; exit 1; fi
	@# This target would call a new orchestration script
	@python3 ../../scripts/run_log_analysis.py $(LOGS)
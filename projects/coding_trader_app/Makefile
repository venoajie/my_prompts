# projects\coding_trader_app\Makefile
# =====================================================================
# Makefile for the "coding_trader_app" Project
# Version: 2.0 (Project-Specific)
# =====================================================================

# --- Project-Specific Configuration ---
PROJECT_NAME := coding_trader_app

# --- Include Common Logic ---
# All common targets (generate-prompt, archive, clean) are inherited from here.
include ../../scripts/common.mk

# --- Target Declarations ---
.PHONY: help end-session generate-manifest-prompt generate-jules-task review-report debug-failed-run
.DEFAULT_GOAL := help

# --- Unified Help Target ---
help:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "   Project: $(PROJECT_NAME) - Automation Tool"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage: make [target] [VARIABLE=value]$(NC)"
	@echo ""
	@echo "$(GREEN)Core Workflows:$(NC)"
	@echo "  make generate-prompt INSTANCE=<path>    - Assembles a final prompt from an instance file. (Inherited)"
	@echo "  make end-session LOG=<path>             - Creates a synthesis prompt from a session log."
	@echo ""
	@echo "$(GREEN)Jules Integration Workflows:$(NC)"
	@echo "  make generate-manifest-prompt INSTANCE=<path> - Generates a prompt to create a JULES_MANIFEST.json."
	@echo "  make generate-jules-task INSTANCE=<path>      - Generates a guided prompt for a generative Jules task."
	@echo "  make review-report REPORT=<path>        - Generates a prompt to analyze a JULES_REPORT.json."
	@echo "  make debug-failed-run REPORT=<path> SOURCE=<path> - Generates a prompt to debug a failed Jules run."
	@echo ""
	@echo "$(GREEN)Instance & Repository Management:$(NC)"
	@echo "  make archive INSTANCE=<name>            - Archives a completed instance with status 'complete'. (Inherited)"
	@echo "  make archive-failed INSTANCE=<name>     - Archives a completed instance with status 'failed'. (Inherited)"
	@echo "  make clean-backups                      - Removes all .bak files from the instances directory. (Inherited)"
	@echo "  make clean                              - Cleans all generated build artifacts for this project. (Inherited)"
	@echo ""

# =====================================================================
# CORE WORKFLOWS
# ====================================================================="

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
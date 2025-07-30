# =====================================================================
# Makefile for the Prompt Engineering Library (PEL)
# Version: 2.0
# =====================================================================

# --- Configuration ---
# Centralize the script name here. This is the Single Source of Truth.
PYTHON_EXEC := $(shell command -v python3 || command -v python)
PEL_TOOLKIT_SCRIPT = scripts/pel_toolkit.py
BUILD_DIR = build
TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)

# ANSI Color codes for pretty output
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

# --- Target Declarations ---
# Default target when just running 'make'
.DEFAULT_GOAL := help

# Consolidated .PHONY declaration is the Single Source of Truth for all non-file targets.
.PHONY: help generate-prompt end-session generate-manifest \
        generate-manifest-prompt generate-jules-task review-report \
        debug-failed-run clean

# =====================================================================
# HELP AND DOCUMENTATION
# =====================================================================
help:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "   Prompt Engineering Library (PEL) - Automation Tool"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(YELLOW)Usage: make [target] [VARIABLE=value]$(NC)"
	@echo ""
	@echo "$(GREEN)Core Workflows:$(NC)"
	@echo "  make generate-prompt INSTANCE=<path>   - Assembles a final prompt XML from an instance file."
	@echo "  make end-session LOG=<path>            - Creates a synthesis prompt from a session log."
	@echo "  make generate-manifest             - (Re)generates the root PEL_AGENTS.md file."
	@echo ""
	@echo "$(GREEN)Jules Integration Workflows (Optional):$(NC)"
	@echo "  make generate-manifest-prompt INSTANCE=<path> - Generates a prompt to create a JULES_MANIFEST.json."
	@echo "  make generate-jules-task INSTANCE=<path>      - Generates a guided prompt for a generative Jules task."
	@echo "  make review-report REPORT=<path>       - Generates a prompt to analyze a JULES_REPORT.json."
	@echo "  make debug-failed-run REPORT=<path> SOURCE=<path> - Generates a prompt to debug a failed Jules run."
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make clean                             - Cleans all generated build artifacts."
	@echo ""

# =====================================================================
# CORE WORKFLOWS
# =====================================================================
generate-prompt:
	@( \
		if [ -z "$(INSTANCE)" ]; then \
			echo "ERROR: Please specify the instance file."; \
			echo "Usage: make generate-prompt INSTANCE=domains/coding_trader_app/instances/your_task.instance.md"; \
			exit 1; \
		fi; \
		mkdir -p $(BUILD_DIR); \
		INSTANCE_BASENAME=$$(basename $(INSTANCE) .instance.md); \
		OUTPUT_FILE=$(BUILD_DIR)/$${INSTANCE_BASENAME}.prompt.xml; \
		echo "Generating prompt for [$(INSTANCE)] -> [$${OUTPUT_FILE}]"; \
		$(PYTHON_EXEC) $(PEL_TOOLKIT_SCRIPT) $(INSTANCE) > $${OUTPUT_FILE}; \
	)

end-session:
	@if [ -z "$(LOG)" ]; then \
		echo "ERROR: Please specify the session log file."; \
		exit 1; \
	fi
	@echo "Synthesizing session log: $(LOG)"
	@( \
		mkdir -p $(BUILD_DIR); \
		SYNTH_INSTANCE_FILE=$(BUILD_DIR)/synthesize-session-$(TIMESTAMP).instance.md; \
		echo "---" > $${SYNTH_INSTANCE_FILE}; \
		echo "domain: prompt_engineering" >> $${SYNTH_INSTANCE_FILE}; \
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
		echo "$(YELLOW)-----------------------------------------------------------------------$(NC)"; \
	)

generate-manifest:
	@echo "Generating PEL_AGENTS.md manifest directly from source files..."
	@$(PYTHON_EXEC) $(PEL_TOOLKIT_SCRIPT) --generate-manifest > PEL_AGENTS.md
	@echo "$(GREEN)PEL_AGENTS.md has been successfully regenerated.$(NC)"

# =====================================================================
# JULES INTEGRATION WORKFLOWS
# =====================================================================
generate-manifest-prompt:
	@if [ -z "$(INSTANCE)" ]; then \
		echo "ERROR: Please specify the instance file for the JIA-1 persona."; \
		exit 1; \
	fi
	@echo "Generating prompt to create a Jules Manifest..."
	@$(MAKE) generate-prompt INSTANCE=$(INSTANCE)

generate-jules-task:
	@if [ -z "$(INSTANCE)" ]; then \
		echo "ERROR: Please specify the instance file for the JTA-1 persona."; \
		echo "Usage: make generate-jules-task INSTANCE=path/to/create-task.instance.md"; \
		exit 1; \
	fi
	@echo "Generating a guided task prompt for Jules..."
	@$(MAKE) generate-prompt INSTANCE=$(INSTANCE)

review-report:
	@if [ -z "$(REPORT)" ]; then \
		echo "ERROR: Please specify the JULES_REPORT.json file."; \
		echo "Usage: make review-report REPORT=path/to/JULES_REPORT.json"; \
		exit 1; \
	fi
	@echo "Generating prompt to review Jules report: $(REPORT)"
	@# This dynamically creates the instance file for the JRI-1 persona
	@REVIEW_INSTANCE_FILE=$(BUILD_DIR)/review-report.instance.md; \
	echo "---" > $${REVIEW_INSTANCE_FILE}; \
	echo "domain: prompt_engineering" >> $${REVIEW_INSTANCE_FILE}; \
	echo "persona_alias: jri-1" >> $${REVIEW_INSTANCE_FILE}; \
	echo "---" >> $${REVIEW_INSTANCE_FILE}; \
	echo "<Mandate><Inject src=\"$(REPORT)\" /></Mandate>" >> $${REVIEW_INSTANCE_FILE}; \
	\
	@$(MAKE) generate-prompt INSTANCE=$${REVIEW_INSTANCE_FILE}

debug-failed-run:
	@if [ -z "$(REPORT)" ]; then \
		echo "ERROR: Please specify the failed JULES_REPORT.json file."; \
		exit 1; \
	fi
	@if [ -z "$(SOURCE)" ]; then \
		echo "ERROR: Please specify the original source file(s) that failed."; \
		exit 1; \
	fi
	@echo "Generating prompt to debug failed run: $(REPORT)"
	@# This dynamically creates an instance file for the DA-1 persona
	@DEBUG_INSTANCE_FILE=$(BUILD_DIR)/debug-run.instance.md; \
	echo "---" > $${DEBUG_INSTANCE_FILE}; \
	echo "domain: coding_trader_app" >> $${DEBUG_INSTANCE_FILE}; \
	echo "persona_alias: da-1" >> $${DEBUG_INSTANCE_FILE}; \
	echo "---" >> $${DEBUG_INSTANCE_FILE}; \
	echo "<Mandate>" >> $${DEBUG_INSTANCE_FILE}; \
	echo "  <Inject src=\"$(REPORT)\" />" >> $${DEBUG_INSTANCE_FILE}; \
	echo "  <Inject src=\"$(SOURCE)\" />" >> $${DEBUG_INSTANCE_FILE}; \
	echo "</Mandate>" >> $${DEBUG_INSTANCE_FILE}; \
	\
	@$(MAKE) generate-prompt INSTANCE=$${DEBUG_INSTANCE_FILE}

# =====================================================================
# WORKFLOW AUTOMATION
# =====================================================================
.PHONY: handoff-plan
handoff-plan:
	@if [ -z "$(PLAN_FILE)" ]; then echo "ERROR: Please set PLAN_FILE."; exit 1; fi
	@if [ -z "$(TARGET_INSTANCE)" ]; then echo "ERROR: Please set TARGET_INSTANCE."; exit 1; fi
	@echo "Injecting plan from [$(PLAN_FILE)] into [$(TARGET_INSTANCE)]..."
	@# This is a robust way to replace a placeholder in a file.
	@# It requires a placeholder like <!-- PASTE_PLAN_HERE --> in the instance file.
	@sed -i.bak -e "/<!-- PASTE_PLAN_HERE -->/r $(PLAN_FILE)" -e "/<!-- PASTE_PLAN_HERE -->/d" $(TARGET_INSTANCE)
	@echo "$(GREEN)✓ Handoff complete. '$(TARGET_INSTANCE)' has been updated.$(NC)"

# =====================================================================
# UTILITIES
# =====================================================================
clean:
	@echo "Cleaning generated artifacts from $(BUILD_DIR)/"
	@rm -rf $(BUILD_DIR)
# =====================================================================
# Makefile for the Prompt Engineering Library (PEL)
# =====================================================================

# --- Configuration ---
# Centralize the script name here. This is the Single Source of Truth.
ASSEMBLER_SCRIPT = scripts/assemble_prompt_v3.2.py
BUILD_DIR = build

# ANSI Color codes for pretty output
GREEN = \033[0;32m
YELLOW = \033[1;33m
BLUE = \033[0;34m
NC = \033[0m

# Default target when just running 'make'
.DEFAULT_GOAL := help

# =====================================================================
# HELP AND DOCUMENTATION
# =====================================================================
.PHONY: help
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
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make clean                             - Cleans all generated build artifacts."
	@echo ""

# =====================================================================
# PROMPT GENERATION & WORKFLOWS
# =====================================================================
.PHONY: generate-prompt
generate-prompt:
	@if [ -z "$(INSTANCE)" ]; then \
		echo "ERROR: Please specify the instance file."; \
		echo "Usage: make generate-prompt INSTANCE=domains/coding_trader_app/instances/your_task.instance.md"; \
		exit 1; \
	fi
	@mkdir -p $(BUILD_DIR)
	@INSTANCE_BASENAME=$$(basename $(INSTANCE) .instance.md); \
	OUTPUT_FILE=$(BUILD_DIR)/$${INSTANCE_BASENAME}.prompt.xml; \
	echo "Generating prompt for [$(INSTANCE)] -> [$${OUTPUT_FILE}]"; \
	python $(ASSEMBLER_SCRIPT) $(INSTANCE) > $${OUTPUT_FILE}

.PHONY: end-session
end-session:
	@if [ -z "$(LOG)" ]; then \
		echo "ERROR: Please specify the session log file."; \
		echo "Usage: make end-session LOG=path/to/session_log.md"; \
		exit 1; \
	fi
	@echo "Synthesizing session log: $(LOG)"
	@# Step 1: Create an instance file for the synthesizer on the fly
	@SYNTH_INSTANCE_FILE=$(BUILD_DIR)/synthesize.instance.md; \
	echo "---" > $${SYNTH_INSTANCE_FILE}; \
	echo "domain: prompt_engineering" >> $${SYNTH_INSTANCE_FILE}; \
	echo "persona_alias: session-synthesizer" >> $${SYNTH_INSTANCE_FILE}; \
	echo "---" >> $${SYNTH_INSTANCE_FILE}; \
	echo "<Mandate><Inject src=\"$(LOG)\" /></Mandate>" >> $${SYNTH_INSTANCE_FILE}; \
	\
	@# Step 2: Generate the prompt FOR the synthesizer
	@SYNTH_PROMPT_FILE=$(BUILD_DIR)/synthesize.prompt.xml; \
	$(MAKE) generate-prompt INSTANCE=$${SYNTH_INSTANCE_FILE}; \
	\
	@echo ""
	@echo "$(YELLOW)--------------------------- ACTION REQUIRED ---------------------------$(NC)"
	@echo "A synthesis prompt has been generated at: $(GREEN)$(SYNTH_PROMPT_FILE)$(NC)"
	@echo "1. Copy the content of this file and execute it with your LLM."
	@echo "2. Save the resulting JSON output to your knowledge_base."
	@echo "$(YELLOW)-----------------------------------------------------------------------$(NC)"

# =====================================================================
# UTILITIES
# =====================================================================
# Renamed for consistency with standard Makefiles
.PHONY: clean
clean:
	@echo "Cleaning generated artifacts from $(BUILD_DIR)/"
	@rm -rf $(BUILD_DIR)
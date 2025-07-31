# projects\prompt_engineering\Makefile

# Makefile for the "prompt_engineering" Project
PEL_TOOLKIT_SCRIPT = ../../scripts/pel_toolkit.py
BUILD_DIR = ../../build/prompt_engineering

.PHONY: help generate-prompt
.DEFAULT_GOAL := help

help:
    @echo "Project: prompt_engineering"
    @echo "  make generate-prompt INSTANCE=<path>"

generate-prompt:
    @mkdir -p $(BUILD_DIR)
    @INSTANCE_BASENAME=$$(basename $(INSTANCE) .instance.md); \
    OUTPUT_FILE=$(BUILD_DIR)/$${INSTANCE_BASENAME}.prompt.xml; \
    python3 $(PEL_TOOLKIT_SCRIPT) $(INSTANCE) > $${OUTPUT_FILE}; \
    echo "✓ Prompt generated in $(BUILD_DIR)"
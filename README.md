---
# The Prompt Engineering Library (PEL)

This repository is a systematic, version-controlled library for managing and deploying high-quality AI prompts. It treats prompts as production source code, subject to the same engineering rigor, including versioning, peer review, and automated composition.

**Core Philosophy:** A prompt is not a command; it is the blueprint for an agent. This library provides the tools and architecture to build a powerful system of specialized AI agents.

---

## Core Architecture

This library is built on a strict architecture designed for maximum reusability, clarity, and scalability.

1.  **The Engine:** A versioned set of core system kernels. A kernel provides the foundational rules, execution protocols, and error boundaries for all tasks. It is domain-agnostic and ensures a consistent standard of quality.
2.  **Domains:** A high-level grouping for a specific project (e.g., `coding_trader_app`). Each domain is a self-contained workspace with its own specialized personas, workflows, and knowledge base.
3.  **Personas:** Reusable, versioned agent blueprints. Personas can inherit from base personas to create specialized agents without duplicating logic.
4.  **Instances:** A specific, disposable task. An instance prompt activates a persona, provides it with knowledge via `<Inject>` tags, and gives it a clear mandate.

## Directory Structure

my-prompt-library/
├── .github/                # CI/CD workflows (e.g., prompt validation)
├── engine/                 # Contains versioned System Kernels
│   └── v1/
│       └── system_kernel.xml
├── domains/                # Contains all specialized work areas
│   └── [domain_name]/
│       ├── personas/         # Domain-specific persona definitions
│       │   ├── base/
│       │   ├── mixins/
│       │   └── specialized/
│       ├── instances/        # Disposable, task-specific instance requests
│       ├── workflows/        # Multi-step chains of instances
│       └── knowledge_base/   # Source data (code, docs) for prompts
│
├── scripts/                # Helper scripts, like the prompt assembler
└── README.md               # This file

## How to Use This Library

### Step 1: Author an Instance File

Navigate to the appropriate domain (e.g., `domains/coding_trader_app/`) and create a new instance file in the `instances/` directory (e.g., `generate-unit-tests.instance.md`). An instance file uses **YAML Frontmatter** to declare its domain and target persona.

To include a file as context, reference it from the domain's `knowledge_base/` using `<Inject src="..."/>`.

**Example: `generate-unit-tests.instance.md`**
```markdown
---
domain: coding_trader_app
persona_alias: ute-1
---

<Mandate>
Generate comprehensive unit tests for the `ReconciliationAgent` class found in the provided source code.
</Mandate>

<Inject src="src/services/executor/deribit/reconciliation_agent.py" />
```

### Step 2: Assemble and Execute the Prompt

Use the `assemble_prompt_v2.py` script to build the full prompt. The script reads the frontmatter, finds the correct persona and engine, handles inheritance, injects knowledge base content, and prints the final, complete prompt.

```bash
# This command assembles the prompt and copies it to your clipboard
python scripts/assemble_prompt_v2.py domains/coding_trader_app/instances/generate-unit-tests.instance.md | pbcopy
```

You can now paste the fully assembled prompt into your preferred AI interface.

---

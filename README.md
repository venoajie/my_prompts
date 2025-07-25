# The Prompt Engineering Library (PEL)

This repository is a systematic, version-controlled library for managing and deploying high-quality AI prompts. It treats prompts as production source code, subject to the same engineering rigor, including versioning, peer review, and automated composition.

**Core Philosophy:** A prompt is not a command; it is the blueprint for an agent. This library provides the tools and architecture to build a powerful system of specialized AI agents.

---

## Core Architecture

This library is built on a strict, principled architecture designed for maximum reusability, clarity, and scalability.

1.  **The Architectural Blueprint:** A single, version-controlled `PEL_BLUEPRINT.md` file at the root of the repository. It is the constitution for the library, defining the intended state, core principles, and architectural rationale.
2.  **The Engine:** A versioned set of core `system_kernel.xml` files. A kernel provides the foundational rules, execution protocols, and error boundaries for all tasks.
3.  **Domains:** Self-contained workspaces for specific projects (e.g., `coding_trader_app`). Each domain has its own specialized personas, workflows, and non-code knowledge base artifacts.
4.  **Personas:** Reusable, versioned agent blueprints defined in individual files. Personas can inherit from base personas to create specialized agents without duplicating logic.
5.  **Instances:** A specific, disposable task definition. An instance prompt activates a persona and provides it with context by injecting files directly from the project's source tree.

## Directory Structure

The repository is organized to enforce the **Single Source of Truth** principle.

```
my-prompt-library/
├── .github/                # CI/CD workflows (e.g., prompt validation)
├── engine/                 # Contains versioned System Kernels
│   └── v1/
│       └── system_kernel.xml
├── domains/                # Contains all specialized work areas
│   └── [domain_name]/
│       ├── personas/         # Domain-specific persona definitions (base/, mixins/, specialized/)
│       ├── instances/        # Disposable, task-specific instance requests
│       ├── workflows/        # Definitions for multi-step tasks
│       └── knowledge_base/   # NON-CODE artifacts (e.g., blueprints, strategy docs)
│
├── scripts/                # Helper scripts, like the prompt assembler
├── src/                    # Example: Your LIVE application source code
│
├── PEL_BLUEPRINT.md        # The architectural constitution for this library
└── README.md               # This file
```

---

## Core Workflows

This library is operated through two primary workflows, both automated by the `assemble_prompt.py` script.

### 1. Executing a Prompt (The Two-Stage Process)

Executing a task is a sophisticated, interactive process designed to prevent errors before they happen.

#### Step 1: Author an Instance File

Navigate to the appropriate domain and create a new instance file (e.g., `instances/generate-unit-tests.instance.md`). The file uses YAML frontmatter to declare its domain and target persona.

To include a file as context, use the `<Inject>` tag with a path relative to the **repository root**. This allows you to reference your live, actively-edited source code directly, with no copying required.

**Example: `generate-unit-tests.instance.md`**
```markdown
---
domain: coding_trader_app
persona_alias: ute-1
---

<Mandate>
Generate comprehensive unit tests for the `ReconciliationAgent` class found in the provided source code.
</Mandate>

<!-- This injects the LIVE source file, not a copy -->
<Inject src="src/services/executor/deribit/reconciliation_agent.py" />
```

#### Step 2: Assemble and Execute the Prompt

Use the `assemble_prompt_v3.0.py` script to build the full prompt. This script now performs a two-stage process:

1.  **Stage 1: Alignment Check (Pre-Flight)**
    The script first makes a fast, low-cost LLM call to a specialized `ALIGNMENT-CHECKER` persona. It compares your mandate against all available personas in the domain. If a better-suited persona is found, it will warn you and offer a chance to switch, preventing you from running a costly task with the wrong agent.

    ```bash
    $ python scripts/assemble_prompt_v3.0.py ...
    [ALIGNMENT_WARNING] The requested persona 'CSA-1' may not be the best fit.
    The persona 'UTE-1' appears to be a much stronger match.
    Proceed with original, or switch? (original/switch): switch
    ```

2.  **Stage 2: Final Assembly**
    Once the correct persona is confirmed, the script assembles the full prompt, injects all file content, and prints the final payload to your terminal, ready to be copied.

    ```bash
    # This command runs the full two-stage process
    python scripts/assemble_prompt_v3.0.py domains/coding_trader_app/instances/generate-unit-tests.instance.md | pbcopy
    ```

### 2. Auditing the Library (Maintaining Health)

To prevent architectural decay, the library includes a built-in audit workflow. This process uses the **PEL Auditor (`PELA-1`)** persona to perform a gap analysis between the `PEL_BLUEPRINT.md` and the actual state of the repository.

This is a periodic health check you should run to receive an actionable report on how to improve your library's structure, scripts, and documentation.

```bash
# Run the built-in audit to get a "State of the Library" report
python scripts/assemble_prompt_v3.0.py domains/prompt_engineering/instances/run-quarterly-audit.instance.md
```

---

## How to Contribute

All changes to this library must be made via a Pull Request (PR) against the `main` branch.

1.  **Branching:** Create a new feature branch (e.g., `feature/add-new-qsa-persona`).
2.  **Architectural Changes:** For fundamental changes to the library's structure or principles, the PR **must** begin by proposing an update to `PEL_BLUEPRINT.md`. The approved blueprint then serves as the specification for the implementation work.
3.  **Make Changes:** Add or modify personas, instances, or scripts according to the blueprint.
4.  **Provide Validation Evidence:** The PR description is **required** to contain proof that your changes work as expected. This includes the path to the instance file used for testing and the full, unedited output from the LLM.
5.  **Peer Review:** At least one other collaborator must review and approve the PR.
```
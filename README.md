# README.md
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

This library is operated through three primary workflows.

### 1. Determining Required Evidence

Before writing an instance file, you must determine which documents the persona needs to perform its task. Follow this four-step protocol:

1.  **Deconstruct the Mandate:** Identify the primary action (e.g., `refactor`, `debug`) and the subjects (e.g., `ReconciliationAgent`, `A1 optimization plan`). This gives you your initial list of artifacts.
2.  **Consult the Persona's Blueprint:** Open the `.persona.md` file for your chosen agent. Its `operational_protocol` explicitly states what it expects to analyze or modify.
3.  **Trace Dependencies:** Review the primary artifacts for dependencies (e.g., `import` statements in code, `volumes` in Docker Compose) to discover secondary evidence.
4.  **Consider Failure Paths:** For debugging or testing, consider what other components are involved if the primary component fails (e.g., error handlers, loggers).

### 2. Executing a Prompt (The Two-Stage Process)

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

Use the `Makefile` to generate the final, complete prompt. This is the most reliable and standardized method.


```bash
# This command generates the prompt and saves it to the build/ directory
make generate-prompt INSTANCE=domains/coding_trader_app/instances/generate-unit-tests.instance.md
```

This will create a file like build/generate-unit-tests.prompt.xml. You can now open this file to review the full prompt before use.

#### Step 3: Execute the Prompt
Copy the contents of the generated .xml file and paste it into your preferred LLM interface.


### 3. Managing and Resuming Sessions (The Handoff Workflow)

To work on a complex task over multiple sessions without losing context or incurring high token costs, use the session synthesis workflow.

#### Step 1: At the end of your session

Save the entire conversation log to a file (e.g., `domains/prompt_engineering/knowledge_base/session_log_01.md`).

#### Step 2: Synthesize the log

Run an instance prompt that activates the `SESSION-SYNTHESIZER` persona. This will read the large log file and produce a small, structured JSON summary.

```bash
# Create an instance file for the synthesizer, then run this command
make generate-prompt INSTANCE=domains/prompt_engineering/instances/synthesize-session.instance.md
```

This will create a file like build/synthesize-session.prompt.xml. Execute this prompt and save the resulting JSON to a file (e.g., knowledge_base/session_synthesis_01.json).

#### Step 3: To resume your session
Use an instance prompt that activates the appropriate persona (e.g., PELA-1) and injects the small, structured session_synthesis_01.json file, not the original large log. This provides the agent with a dense, high-signal summary of all previous decisions and outcomes.

### 4. Delegated Execution via Jules (Optional Advanced Workflow)

For complex tasks, you can delegate the final implementation to an external agent like Jules. This workflow has two modes, depending on your task.

#### Mode A: Executing Pre-Generated Code (Manifest-based)

Use this mode when you have already used a PEL persona (like `CSA-1`) to generate and approve a set of code artifacts.

1.  **Generate a Jules Manifest:** Use the `JIA-1` (Jules Integration Architect) persona to create a machine-readable `JULES_MANIFEST.json` instruction file from your generated code.
    ```bash
    make generate-manifest-prompt INSTANCE=path/to/create-manifest.instance.md
    ```
2.  **Execute with Jules:** Provide the resulting `JULES_MANIFEST.json` to the Jules agent.

#### Mode B: Guiding a Generative Task

Use this mode for tasks like writing documentation, refactoring a class, or creating a new feature from scratch.

1.  **Generate a Guided Task Prompt:** Use the `JTA-1` (Jules Task Architect) persona to convert your high-level goal into a perfect, context-rich prompt for Jules.
    ```bash
    make generate-jules-task INSTANCE=path/to/create-task.instance.md
    ```
2.  **Use the Output:** The generated prompt will include both a "Guided Prompt for Jules" and a "Recommended Persona and Prompt" section to help you frame your interaction effectively.

#### Reviewing the Results

After either mode, Jules may provide a `JULES_REPORT.json`. Use the `JRI-1` persona to get a human-readable summary of the outcome.
```bash
make review-report REPORT=path/to/JULES_REPORT.json


### 5. Auditing the Library (Maintaining Health)

To prevent architectural decay, the library includes a built-in audit workflow. This process uses the PEL Auditor (PELA-1) persona to perform a gap analysis between the PEL_BLUEPRINT.md and the actual state of the repository.

This is a periodic health check you should run to receive an actionable report on how to improve your library's structure, scripts, and documentation.

```bash
# Run the built-in audit to get a "State of the Library" report
make generate-prompt INSTANCE=domains/prompt_engineering/instances/run-quarterly-audit.instance.md
```


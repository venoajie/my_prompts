# README.md

# The Prompt Engineering Library (PEL)

This repository is a systematic, version-controlled library for managing and deploying high-quality AI prompts. It treats prompts as production source code, subject to the same engineering rigor, including versioning, peer review, and automated composition.

**Core Philosophy:** A prompt is not a command; it is the blueprint for an agent. This library provides the tools and architecture to build a powerful system of specialized AI agents across multiple, independent projects.

---

## Core Architecture: Templates & Instances

This library is built on a "Templates & Instances" architecture designed for maximum reusability, clarity, and scalability.

*   **/templates:** Contains reusable, generic project structures. A template defines the base personas, mixins, and governance files (like a `Makefile.template`) for a specific type of work (e.g., a standard coding project).
*   **/projects:** Contains specific, self-contained project implementations. Each project is initialized from a template and then customized with its own specialized personas, knowledge base, and a `DOMAIN_BLUEPRINT.md` that governs its unique architecture.

This model ensures that project-specific complexity is isolated, while proven patterns are easily reused.

### Directory Structure

The repository is organized to enforce the **Single Source of Truth** and **Domain Isolation** principles.

```
my-prompt-library/
├── .github/              # CI/CD workflows (e.g., persona validation)
├── build/                # Generated, ephemeral artifacts. Not version-controlled.
├── engine/               # Contains versioned System Kernels (e.g., system_kernel.xml)
│
├── projects/             # Contains all self-contained project instances.
│   └── [project_name]/
│       ├── .domain_meta          # Links project to its template.
│       ├── DOMAIN_BLUEPRINT.md   # The architectural constitution for THIS project.
│       ├── Makefile              # Project-specific automation commands.
│       ├── instances/            # Disposable, task-specific instance requests.
│       ├── knowledge_base/       # Curated, non-code artifacts for the project.
│       └── personas/             # Project-specific personas (specialized/).
│
├── templates/            # Contains reusable project templates.
│   └── [template_name]/
│       ├── DOMAIN_BLUEPRINT.md.template # Template for a project's blueprint.
│       ├── Makefile.template            # Template for a project's Makefile.
│       └── personas/                    # Reusable personas (base/, mixins/).
│
├── scripts/              # Global helper scripts (pel_toolkit.py, pel-init.sh).
│
├── .gitignore
├── Makefile              # Root dispatcher Makefile.
├── PEL_BLUEPRINT.md      # The architectural constitution for the ENTIRE library.
└── README.md             # This file.
```

---

## Core Workflows

This library is operated through a root **dispatcher `Makefile`**.

### 1. Creating a New Project

To create a new, self-contained project from a template, use the `new-project` command.

```bash
# This command scaffolds a new project named 'my_new_app'
# using the 'domain_coding_generic' template.
make new-project TEMPLATE=domain_coding_generic NAME=my_new_app
```
This will create the directory `projects/my_new_app` with all the necessary files to get started.

### 2. Executing a Prompt within a Project

All prompt-related commands are now dispatched to the project's local `Makefile`. You must specify the target project using the `PROJECT` variable.

#### Step 1: Author an Instance File

Navigate to the appropriate project and create a new instance file (e.g., `projects/coding_trader_app/instances/generate-unit-tests.instance.md`).

**Example: `generate-unit-tests.instance.md`**
```markdown
---
persona_alias: ute-1
---

<Mandate>
Generate comprehensive unit tests for the `ReconciliationAgent` class.
</Mandate>

<!-- The toolkit automatically resolves paths from the repo root -->
<Inject src="src/services/executor/deribit/reconciliation_agent.py" />
```

#### Step 2: Assemble and Execute the Prompt

Use the root `Makefile` to dispatch the `generate-prompt` command to the correct project.

```bash
# This command is run from the repository root.
# It tells the root Makefile to execute the 'generate-prompt' target
# inside the 'coding_trader_app' project's Makefile.

make generate-prompt PROJECT=coding_trader_app INSTANCE=instances/generate-unit-tests.instance.md
```

This will create a file in the project-specific build directory (e.g., `build/coding_trader_app/generate-unit-tests.prompt.xml`). You can now copy the content of this file and execute it in your LLM interface.

### 3. Other Project-Specific Commands

Other complex workflows, like `end-session` or `review-report`, are defined within the project's own `Makefile` and are executed using the same dispatch pattern:

```bash
# Example: Ending a session for the 'coding_trader_app' project
make end-session PROJECT=coding_trader_app LOG=path/to/session.log
```

### 4. Validating the Library

To ensure the architectural integrity of all personas and mixins across all templates and projects, run the global `validate` command.

```bash
make validate
```
This is a critical CI/CD step to prevent architectural decay.
```

*   **Command:**
    1.  Open the root `README.md` in your editor.
    2.  Delete all existing content.
    3.  Paste the new content above and save the file.

*   **Verification:** The new `README.md` should accurately reflect the current architecture.

Please execute this action. Once complete, confirm, and we will proceed to **Step 1.2: Create the New Root `PEL_BLUEPRINT.md`**.
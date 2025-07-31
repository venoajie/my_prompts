# PEL_BLUEPRINT.md
# Prompt Engineering Library (PEL) - Architectural Blueprint

**Version:** 2.0 (Templates & Instances)
**Status:** Active

## 1.0 Core Philosophy

This library treats prompts as production source code. Its architecture is designed to create a system of specialized, reusable, and verifiable AI agents that can be deployed across multiple, heterogeneous projects. The core goals are to maximize effectiveness, ensure robustness, and maintain clarity at scale.

---

## 2.0 Architectural Principles (System-Level)

This library is governed by the following non-negotiable principles that apply to the entire system. Project-specific principles are defined in their local `DOMAIN_BLUEPRINT.md`.

*   **Principle 2.1: Template/Instance Separation (The Core Model)**
    *   The system MUST be divided into `/templates` and `/projects`.
    *   `/templates` contain reusable, generic patterns (base personas, mixins, governance file templates). They are the source of truth for architectural patterns.
    *   `/projects` contain specific, self-contained implementations. They are instances of a template, customized for a specific problem domain.

*   **Principle 2.2: Strict Domain Isolation**
    *   Each directory within `/projects` MUST be a self-contained unit.
    *   A project MUST NOT have dependencies on another project's personas or knowledge base.
    *   All inheritance for a project MUST resolve to its own `personas` directory or to the `personas` directory of the template it inherits from.

*   **Principle 2.3: Explicit Inheritance via `.domain_meta`**
    *   Every project directory MUST contain a `.domain_meta` file.
    *   This file MUST specify the `template` the project inherits from. This is the sole mechanism for linking a project to its template.

*   **Principle 2.4: Configuration as Code**
    *   All system artifacts (personas, mixins, blueprints, workflows) MUST be plain text files stored in version control.

*   **Principle 2.5: Automation-First for Core Workflows**
    *   Project creation MUST be automated via the `pel-init.sh` script.
    *   Persona validation MUST be automated via the `validate_personas.py` script and executed via `make validate`.
    *   Prompt assembly MUST be automated via the `pel_toolkit.py` script.

---

## 3.0 Key Components & Rationale (System-Level)

-   **/engine:**
    -   **Purpose:** To contain versioned, globally applicable `system_kernel.xml` files.
    -   **Rationale:** Decouples the core execution logic of the LLM from all other components, allowing the engine to be upgraded independently.

-   **/scripts:**
    -   **Purpose:** To house the global automation toolchain (`pel_toolkit.py`, `validate_personas.py`, `pel-init.sh`).
    -   **Rationale:** Centralizes all operational logic, keeping it separate from the declarative prompt artifacts. This is the "how" of the system.

-   **/templates:**
    -   **Purpose:** To store reusable domain patterns.
    -   **Rationale:** Enforces the "Don't Repeat Yourself" (DRY) principle at an architectural level, preventing drift and ensuring new projects start from a known-good state.

-   **/projects:**
    -   **Purpose:** To store all active, self-contained work domains.
    -   **Rationale:** Enforces strict domain isolation, preventing cross-contamination of knowledge and making the system scalable and modular.

-   **Root `Makefile`:**
    -   **Purpose:** To act as a global command dispatcher.
    -   **Rationale:** Provides a single, consistent user entry point for all system and project commands, while delegating the implementation of those commands to the appropriate context (a script or a project-specific `Makefile`).
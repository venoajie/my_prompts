
### **Technical Specification & Integration Plan: PEL-Jules Module**

**Version:** 2.0 (Finalized)
**Status:** Active
**Location:** `domains/prompt_engineering/knowledge_base/SPEC-JULES-INTEGRATION-V2.md`

#### **1.0 Overview & Guiding Principles**

This document defines the final architecture for integrating the Jules coding agent as an optional, external execution engine for the Prompt Engineering Library (PEL).

1.  **Optionality:** The Jules integration is a pluggable module, invoked via specific `Makefile` targets. The PEL's core workflows are not dependent on it.
2.  **Safety and Precision:** Interactions with Jules are designed to be precise and deterministic, favoring machine-readable instructions and explicit context to mitigate agent error.

#### **2.0 Jules Technical Profile**

*   **Core Function:** An asynchronous, GitHub-integrated agent that executes tasks (bug fixes, feature implementation) in a fresh, secure VM.
*   **Execution Environment:** Clones the repo, installs dependencies via setup scripts, and operates with internet access. It cannot run long-lived, interactive processes.
*   **Native Context Ingestion:** Jules automatically searches for and reads a root-level `AGENTS.md` file to understand project-specific commands and conventions.

#### **3.0 Integration Architecture: A Dual-Mode Handoff**

The integration is architected around two distinct interaction modes, ensuring the right tool is used for each task.

**3.1 Mode A: Manifest-Based Execution (For Deterministic Tasks)**

This is the preferred mode for its safety. It is used for tasks with a clear, pre-approved implementation plan.

*   **Workflow:**
    1.  A PEL persona (`CSA-1`, `DA-1`) generates a plan and code artifacts.
    2.  The user invokes `make generate-manifest-prompt INSTANCE=<path>` with the `JIA-1` persona.
    3.  `JIA-1` produces a `JULES_MANIFEST.json` file, validating it against the schema defined in `/docs/system_contracts.yml`.
*   **Handoff Mechanism:** The user provides Jules with a prompt that instructs it to act as a "Manifest Executor." The prompt contains the full `JULES_MANIFEST.json` and directs Jules to parse and apply the operations precisely as listed.

**3.2 Mode B: Guided Task Generation (For Exploratory Tasks)**

This mode is used for generative tasks where the exact implementation path is unknown.

*   **Workflow:**
    1.  The user invokes `make generate-jules-task INSTANCE=<path>` with the `JTA-1` persona.
    2.  `JTA-1` ingests the user's goal and context files.
    3.  It produces a structured, natural-language prompt formatted using the "Persona, Context, Task" (PCT) framework.
*   **Handoff Mechanism:** The user provides the generated PCT prompt directly to Jules.

#### **4.0 Key Artifacts & Data Contracts**

This integration relies on the following high-quality, machine-readable artifacts:

*   **`/PROJECT_BLUEPRINT_V3.0.md` (The Constitution):** The primary source of truth for system architecture, data flows, and design rationale. It is the foundational context for any large-scale refactoring task given to Jules.
*   **`/AGENTS.md` (The Operator's Manual):** The definitive source of executable commands for testing, linting, dependency management, and database migrations. Jules will ingest this file natively to inform its plans.
*   **`/docs/system_contracts.yml` (The Data Dictionary):** The canonical, machine-readable schema for all data contracts, including Redis streams, queues, and the structure of the `JULES_MANIFEST.json` itself.

#### **5.0 Implementation Plan & Final Handoff**

**5.1 Current Status (As of 2025-07-30)**

*   **COMPLETE:** All core documentation (`Blueprint`, `AGENTS.md`, `Contracts`) has been refactored to a machine-first standard suitable for AI agent consumption.
*   **COMPLETE:** Core personas (`JIA-1`, `JTA-1`, `JRI-1`, `DA-1`) are defined and aligned with the integration architecture.
*   **COMPLETE:** `Makefile` targets exist for the primary integration workflows.

**5.2 Outstanding Tasks (Action Plan)**

1.  **[BLOCKER] Resolve Architectural Ambiguities:**
    *   **Action:** Prioritize the resolution of the two open issues documented in `AMBIGUITY_REPORT.md`:
        1.  Clarify and refactor the "Inconsistent System State Handling" logic.
        2.  Define and implement the "`Executor` Multi-Exchange Path."
    *   **Rationale:** These ambiguities represent a critical risk. Tasking Jules to work on the `executor` before they are resolved will likely result in flawed or incomplete work. This is a prerequisite for safe integration.

2.  **[ROBUSTNESS] Implement Security & Constraint Guardrails:**
    *   **Action:** Update the `operational_protocol` for the `JIA-1` and `JTA-1` personas. Add a final validation step: "Review the generated output for violations of Jules's known constraints (e.g., long-running commands, shell command safety) and add an explicit `<!-- WARNING: ... -->` to the output if any are found."
    *   **Rationale:** This adds a critical safety layer, making the PEL a more responsible partner in the "Brain-to-Hands" workflow.

3.  **[MAINTENANCE] Automate `AGENTS.md` Generation:**
    *   **Action:** Implement the `Agent Manifest Documenter for Jules (AMD-J-1)` persona and a corresponding `make generate-jules-agents-md` target.
    *   **Rationale:** While the current, manually-crafted `AGENTS.md` is excellent, it is at risk of becoming stale as the project evolves. Automating its generation from a source of truth (e.g., the `Makefile` itself) ensures it remains accurate over the long term, preventing future agent errors.

---

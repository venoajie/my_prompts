# PEL_BLUEPRINT.md
# Prompt Engineering Library (PEL) - Architectural Blueprint

**Version:** 1.1
**Status:** Active

## 1. Core Philosophy

This library treats prompts as production source code. Its architecture is designed to create a system of specialized, reusable, and verifiable AI agents. The core goals are to maximize effectiveness, ensure robustness, and maintain clarity at scale.

---

## 2. Architectural Principles


This library is governed by the following non-negotiable principles:
-   **Single Source of Truth (SSoT):** There must be only one canonical location for any piece of information or code. Application source code lives in `src/`, persona definitions live in `domains/[domain]/personas/`, etc. There must be no duplication.
-   **Separation of Concerns:** The system is strictly decoupled. The Engine (how the system thinks) is separate from the Personas (who is thinking). Personas (the agent blueprint) are separate from Instances (the specific task).
-   **Configuration as Code:** All system artifacts, including personas and workflows, are plain text files (.md, .xml, .py) stored in version control.
-   **Automation First:** Manual, repetitive processes must be automated via scripts to reduce human error and increase efficiency.
-   **Strict & Accurate Evidence Contracts:** Personas **MUST** declare their expected input artifacts via the `expected_artifacts` frontmatter. These declarations must be **specific, accurate, and unique** to the persona's function. Generic or incorrect declarations are a violation of this principle.
---

## 3. Key Components & Rationale


-   **/engine:**
    -   **Purpose:** To contain the versioned, domain-agnostic `system_kernel.xml` files.
    -   **Rationale:** Decouples the core execution logic from the personas, allowing the engine to be upgraded independently.
-   **/domains:**
    -   **Purpose:** To create isolated workspaces for different problem areas.
    -   **Rationale:** Prevents cross-contamination of personas and knowledge bases, ensuring modularity.
-   **/domains/[domain]/personas:**
    -   **Purpose:** To store individual persona definition files, structured into a clear inheritance and composition hierarchy.
    -   **Structure:**
        -   `base/`: Foundational base personas (e.g., `BTAA-1`) that define broad behavioral patterns.
        -   `mixins/`: Reusable, non-instantiable collections of directives (e.g., `CODEGEN-STANDARDS-1`) that can be composed into other personas.
        -   `specialized/`: The final, concrete agent personas that inherit from `base/` and can include `mixins/`.
    -   **Rationale:** Models the inheritance and composition hierarchy on the filesystem, making relationships explicit and promoting reuse.
-   **/scripts:**
    -   **Purpose:** To house the automation toolchain, primarily `pel_toolkit.py`.
    -   **Rationale:** Centralizes all operational logic, keeping it separate from the declarative prompt artifacts.

---

## 4. Core Workflows
-   **Evidence Gathering:** A formal, four-step protocol for determining which artifacts to provide to a prompt.
-   **Prompt Assembly (Two-Stage):** The `pel_toolkit.py` script executes a two-stage process: Alignment Check and Final Assembly.
-   **Session Handoff & Synthesis:** A formal handoff process using the `SESSION-SYNTHESIZER` persona to distill raw logs into a compact JSON artifact.
-   **Agent Manifest Generation:** The `PEL_AGENTS.md` file is generated via the automated `make generate-manifest` target.
-   **Persona Schema Validation (CI/CD):** To ensure robustness, all `.persona.md` files **MUST** be validated as part of the CI/CD pipeline. This check ensures that the YAML frontmatter is well-formed, contains all required keys, and that `expected_artifacts` declarations are specific and non-generic.
-   **PEL Audit Loop:** The `PELA-1` persona is used to perform a periodic, holistic audit of the library itself, using this blueprint as its primary source of truth.

-   **Delegated Execution (Jules Integration):** The PEL supports a "Brain-to-Hands" workflow with the external execution agent, Jules. This integration is governed by the following critical principles:
    -   **Principle: Commit-Locked Execution:** To ensure determinism and context integrity, all interactions with Jules **MUST** be locked to a specific Git commit hash. The assembly script is responsible for automatically injecting the current `HEAD` commit hash into the prompt context. The Jules-facing personas (`JIA-1`, `JTA-1`) are responsible for instructing Jules to `git checkout` this specific hash before performing any operations. This eliminates the risk of operating on a stale or incorrect version of the codebase.
    -   **Principle: Dual-Mode Interaction:** The integration operates in two distinct, mutually exclusive modes to ensure maximum effectiveness and safety.

    1.  **Mode A: Manifest-Based Execution (Deterministic Tasks):** For pre-approved, deterministic changes. This is the **preferred mode for safety and reliability.**
        -   **Trigger:** The human operator uses the `JIA-1` persona.
        -   **Input:** An implementation plan, generated code artifacts, and the current commit hash (injected by the toolchain).
        -   **Output:** A `JULES_MANIFEST.json` file that includes the `commit_hash`, and a guided prompt instructing Jules to check out that hash before executing the manifest.

    2.  **Mode B: Guided Task Generation (Exploratory Tasks):** For generative or exploratory tasks.
        -   **Trigger:** The human operator uses the `JTA-1` persona.
        -   **Input:** A high-level goal, key context files, and the current commit hash (injected by the toolchain).
        -   **Output:** A guided, natural-language prompt that instructs Jules to first check out the specified commit hash before proceeding with the task.
-   **Jules Self-Correction Loop:** To enhance resilience, the PEL formalizes a closed-loop error correction workflow.
    1.  **Failure:** Jules encounters an error (e.g., a failing test) during manifest execution and generates a `JULES_REPORT.json`.
    2.  **Ingestion & Diagnosis:** The operator uses `make debug-failed-run` to trigger the `DA-1` (Debugging Analyst) persona, which ingests the `JULES_REPORT.json` and original source files to diagnose the root cause.
    3.  **Resolution:** The `DA-1` produces a new, corrected implementation plan.
    4.  **Re-execution:** The corrected plan is passed to `JIA-1` to generate a new, valid `JULES_MANIFEST.json`, restarting the execution workflow.
-   **Jules Capabilities Audit:** To maintain alignment, the `PELA-1` (PEL Auditor) persona is tasked with periodically ingesting the `JULES_CAPABILITIES.json` file to ensure the functionality exposed by `JIA-1` and `JTA-1` has not diverged from Jules's supported toolset.
# PEL_BLUEPRINT.md
# Prompt Engineering Library (PEL) - Architectural Blueprint

**Version:** 1.1
**Status:** Active

## 1. Core Philosophy

This library treats prompts as production source code. Its architecture is designed to create a system of specialized, reusable, and verifiable AI agents. The core goals are to maximize effectiveness, ensure robustness, and maintain clarity at scale.

---

## 2. Architectural Principles

This library is governed by the following non-negotiable principles:
-   **Single Source of Truth (SSoT):** There must be only one canonical location for any piece of information or code. Application source code lives in src/, persona definitions live in domains/[domain]/personas/, etc. There must be no duplication.
-   **Separation of Concerns:** The system is strictly decoupled. The Engine (how the system thinks) is separate from the Personas (who is thinking). Personas (the agent blueprint) are separate from Instances (the specific task). Strategy Design (the "what") is separate from Code Implementation (the "how").
-   **Configuration as Code:** All system artifacts, including personas and workflows, are plain text files (.md, .xml, .py) stored in version control.
-   **Automation First:** Manual, repetitive processes (like metadata generation or prompt assembly) must be automated via scripts to reduce human error and increase efficiency.
-   **Declarative Evidence Requirements:** To improve robustness and guide users, personas SHOULD declare their expected input artifacts. This allows for automated validation by the assembly toolchain to ensure an agent is provided with the necessary context to perform its function.
---

## 3. Key Components & Rationale

-   **/engine:**
    -   **Purpose:** To contain the versioned, domain-agnostic `system_kernel.xml` files.
    -   **Rationale:** Decouples the core execution logic from the personas, allowing the engine to be upgraded independently.
-   **/domains:**
    -   **Purpose:** To create isolated workspaces for different problem areas (e.g., `coding_trader_app`, `prompt_engineering`).
    -   **Rationale:** Prevents cross-contamination of personas and knowledge bases, ensuring the system remains modular and scalable.
-   **/domains/[domain]/personas:**
    -   **Purpose:** To store individual persona definition files, structured into `base/`, `mixins/`, and `specialized/`.
    -   **Rationale:** Models the inheritance hierarchy on the filesystem, making relationships explicit and promoting reuse.
-   **/scripts:**
    -   **Purpose:** To house the automation toolchain, primarily `assemble_prompt.py`.
    -   **Rationale:** Centralizes all operational logic, keeping it separate from the declarative prompt artifacts.

---

## 4. Core Workflows
-   **Evidence Gathering:** The process of determining which artifacts to provide to a prompt is governed by a formal, four-step protocol (Deconstruct Mandate, Consult Persona, Trace Dependencies, Consider Failure Paths), as documented in the root `README.md`.
-   **Prompt Assembly (Two-Stage):** The `assemble_prompt.py` script executes a two-stage process:
    1.  **Alignment Check:** A fast, lightweight LLM call to the `ALIGNMENT-CHECKER` persona to validate that the chosen agent is appropriate for the mandate.
    2.  **Final Assembly:** Construction of the full prompt payload, injecting the chosen persona and all necessary knowledge base artifacts.  
-   **Session Handoff & Synthesis:** To maintain context across long-running collaborations without exceeding token limits, a formal handoff process is used. At the end of a session, the `SESSION-SYNTHESIZER` persona is used to distill the raw conversation log into a compact, structured JSON artifact. This artifact, not the full log, is used to resume the session, ensuring token efficiency and context integrity. This process is automated via the `make end-session` target.
-   **Delegated Execution (Optional Jules Integration):** The PEL supports a "Brain-to-Hands" workflow with external execution agents like Jules. This workflow operates in two distinct modes:
    1.  **Manifest-based Execution:** For pre-approved, deterministic changes. The `JIA-1` persona generates a machine-readable `JULES_MANIFEST.json` which is passed to the agent for execution.
    2.  **Guided Task Generation:** For generative or exploratory tasks. The `JTA-1` persona takes a high-level user goal and generates a guided, natural-language prompt for the agent. This process includes meta-coaching to help the human user interact with the agent effectively.
    A two-way communication channel is supported via a `JULES_REPORT.json` artifact, which can be ingested by the `JRI-1` persona.
-   **PEL Audit Loop:** The `PELA-1` persona is used to perform a periodic, holistic audit of the library itself, using this blueprint as its primary source of truth.
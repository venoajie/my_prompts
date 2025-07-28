# Prompt Engineering Library (PEL) - Architectural Blueprint

**Version:** 1.1
**Status:** Active

## 1. Core Philosophy

This library treats prompts as production source code. Its architecture is designed to create a system of specialized, reusable, and verifiable AI agents. The core goals are to maximize effectiveness, ensure robustness, and maintain clarity at scale.

---

## 2. Architectural Principles

This library is governed by the following non-negotiable principles:
-   **Single Source of Truth (SSoT):** ...
-   **Separation of Concerns:** ...
-   **Configuration as Code:** ...
-   **Automation First:** ...
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
-   **PEL Audit Loop:** The `PELA-1` persona is used to perform a periodic, holistic audit of the library itself, using this blueprint as its primary source of truth.
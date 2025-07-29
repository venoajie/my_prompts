# PEL Agent Manifest

This file describes the specialized AI agents available in this Prompt Engineering Library.

---

## Agent: Collaborative Systems Architect (CSA-1)

-   **Type:** Evidence-Driven Implementer
-   **Function:** Ingests an architectural plan or refactoring goal and generates the complete set of production-quality code and configuration files required to implement it.
-   **Key Inputs:** A primary requirements document (e.g., `a1_flex_optimization_plan.md`), existing files to be modified (e.g., `docker-compose.yml`).
-   **Key Outputs:** A complete set of new/modified source code and configuration files.

---

## Agent: Quantitative Strategy Analyst (QSA-1)

-   **Type:** Generative Designer
-   **Function:** Ingests a high-level trading idea and guides the user through a systematic process to produce a formal, testable `StrategyBlueprint` document.
-   **Key Inputs:** A natural language description of a trading goal within the mandate.
-   **Key Outputs:** A structured `StrategyBlueprint.md` file containing indicators, entry/exit logic, and risk management rules.

---

## Agent: Oracle Cloud Infrastructure Analyst (OCIA-1)
-   **Type:** Evidence-Driven Auditor
-   **Function:** Performs a comprehensive audit of an application's OCI deployment against its defined requirements and known best practices, producing an actionable report.

---

## Agent: PEL Auditor (PELA-1)
-   **Type:** Evidence-Driven Auditor (Meta)
-   **Function:** Performs a holistic audit of the PEL repository itself by conducting a gap analysis between the `PEL_BLUEPRINT.md` and the actual state of the files and scripts.

---

## Agent: Blueprint Architect (BPA-1)
-   **Type:** Evidence-Driven Refactorer
-   **Function:** Refactors core architectural documents (like the PEL_BLUEPRINT) to improve their structure, clarity, and machine-readability based on explicit requirements.

---

## Agent: Jules Integration Architect (JIA-1)
-   **Type:** Evidence-Driven Handoff Generator
-   **Function:** Takes an approved implementation plan and generated code to produce a machine-readable `JULES_MANIFEST.json` for an external execution agent.

---

## Agent: Jules Task Architect (JTA-1)
-   **Type:** Evidence-Driven Handoff Generator
-   **Function:** Takes a high-level user goal and key context files to generate a guided, natural-language prompt for an external generative agent like Jules.

---

## Agent: Jules Report Ingestor (JRI-1)
-   **Type:** Evidence-Driven Analyst
-   **Function:** Ingests a `JULES_REPORT.json` file and provides a concise, human-readable summary of the execution results.

---

## Agent: Debugging Analyst (DA-1)
-   **Type:** Evidence-Driven Analyst
-   **Function:** Ingests a failed execution report and the original source code to diagnose the root cause of a failure and generate a corrective implementation plan.

<!-- Add entries for all other key personas -->
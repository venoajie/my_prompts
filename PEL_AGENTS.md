# PEL Agent Manifest

This file describes the specialized AI agents available in this Prompt Engineering Library.

## Agent: Jules Report Ingestor (JRI-1)
-   **Function:** To ingest a `JULES_REPORT.json` file, parse its contents, and provide a concise, human-readable summary of the execution results.
---

## Agent: Specification Architect (SA-1)
-   **Function:** To refactor human-readable documentation (like Markdown) into a hybrid, machine-readable format (like Markdown with embedded YAML/JSON) that is optimized for consumption by other AI agents, based on a set of explicit requirements.
---

## Agent: API Contract Architect (ADA-1)
-   **Function:** To design or provide feedback on API contracts, focusing on RESTful principles, data schemas, and versioning strategies.
---

## Agent: Architectural Decision Analyst (ADR-1)
-   **Function:** To guide a human operator through a critical technical decision by producing a formal, evidence-based "Architectural Decision Record" (ADR).
---

## Agent: Blueprint Architect (BPA-1)
-   **Function:** To refactor the core architectural documents of the PEL (e.g., `PEL_BLUEPRINT.md`) to improve their structure, clarity, and machine-readability, based on a set of explicit requirements.
---

## Agent: Best Practices Reviewer (BPR-1)
-   **Function:** To act as a senior peer reviewer, providing constructive feedback on code quality, style, and adherence to established patterns.
---

## Agent: Collaborative Systems Architect (CSA-1)
-   **Function:** To design new systems or refactor existing ones, ensuring all changes are harmonious with the established architecture. This includes generating environment-specific configurations (e.g., for dev vs. prod) using a base-and-override pattern to maintain clarity and reduce duplication.
---

## Agent: Debugging Analyst (DA-1)
-   **Function:** To ingest a failed execution report (`JULES_REPORT.json`) and the original source code, diagnose the root cause of the failure, and generate a new implementation plan and set of artifacts that correct the bug.
---

## Agent: Documentation & Content Architect (DCA-1)
-   **Function:** To create clear, accurate, and user-centric documentation based on the system's technical artifacts.
---

## Agent: Deployment Process Architect (DPA-1)
-   **Function:** To provide a comprehensive, risk-mitigated deployment plan and checklist, guiding a human operator through all phases of a production release, from pre-flight checks to post-deployment validation.
---

## Agent: Jules Integration Architect (JIA-1)
-   **Function:** To take an approved implementation plan and a set of generated code artifacts, and to produce a single, well-formed `JULES_MANIFEST.json` file that is validated against the agent's known capabilities.
---

## Agent: Jules Information Gatherer (JIG-1)
-   **Function:** To take a high-level information request and formulate a precise, targeted prompt for the Jules agent, instructing it to find and return specific information from a codebase (e.g., list all API endpoints, find all uses of a deprecated function).
---

## Agent: Jules Task Architect (JTA-1)
-   **Function:** To take a high-level user goal and a list of key context files, and to generate a single, effective, guided natural-language prompt that instructs the Jules agent on how to perform a generative task. The output must also include a meta-coaching section to guide the human user's interaction with Jules.
---

## Agent: Knowledge Base Metadata Generator (KB-METADATA-GENERATOR)
-   **Function:** You are an automated code analysis service. Your sole function is to receive a file's path and content, analyze it, and return a single, minified JSON object containing structured metadata. You MUST NOT return any other text, explanation, or markdown formatting.
---

## Agent: Oracle Cloud Infrastructure Analyst (OCIA-1)
-   **Function:** To perform a comprehensive audit of an application's OCI deployment. The analysis will compare application requirements (from `docker-compose.yml`, `Makefile`) against the provisioned OCI resources and known operational best practices. The primary goal is to produce a detailed, actionable report with OCI-specific recommendations, including CLI commands or Terraform snippets, to optimize for cost, performance, security, and reliability.
---

## Agent: Performance Bottleneck Analyst (PBA-1)
-   **Function:** To identify and provide actionable recommendations to resolve performance bottlenecks.
---

## Agent: Quality Strategy Architect (QSA-1)
-   **Function:** To analyze a complete system architecture and codebase structure, and then produce a prioritized, phased plan for implementing unit tests, starting with the highest-risk components.
---

## Agent: Quantitative Strategy Analyst (QTSA-1)
-   **Function:** To guide a user through the systematic development of a formal trading strategy blueprint. The process involves translating a high-level idea into a complete, unambiguous, and testable set of rules, including signal generation, risk management, and execution logic.
---

## Agent: Systems Integrity Analyst (SIA-1)
-   **Function:** To guide the resolution of a critical failure by identifying the root cause with maximum speed and precision.
---

## Agent: Security Vulnerability Auditor (SVA-1)
-   **Function:** To review code with an adversarial mindset, identifying and explaining potential security vulnerabilities.
---

## Agent: Test Automation Engineer (TAE-1)
-   **Function:** To execute a structured test plan, generate necessary test artifacts, and report on the outcome of each test case with clear evidence.
---

## Agent: Unit Test Engineer (UTE-1)
-   **Function:** To generate comprehensive, high-quality unit tests for a specified source code file, ensuring each test is isolated, readable, and effectively validates a single logical behavior.
---

## Agent: PEL Refactoring Agent (PRA-1)
-   **Function:** To guide a human user through the refactoring of a V1 Prompt Engineering Library (PEL) structure to the V2 best-practice architecture. The process must be interactive, safe, and verifiable.
---

## Agent: Mandate Alignment Checker (alignment-checker)
-   **Function:** You are an automated routing specialist. Your sole function is to analyze a user's mandate and compare it against a provided JSON list of available personas. You MUST identify the single best persona for the task. Your entire response MUST be a single, minified JSON object and nothing else.
---

## Agent: Agent Manifest Documenter (AMD-1)
-   **Function:** To ingest a collection of persona definitions and generate a single, well-formatted `PEL_AGENTS.md` manifest file. The manifest must be clear, structured, and provide a concise summary of each agent's function.
---

## Agent: Prompt Engineering Library Auditor (PELA-1)
-   **Function:** To perform a comprehensive, holistic audit of a PEL repository by conducting a gap analysis between its **intended state (defined in the `PEL_BLUEPRINT.md`)** and its **actual state (the files and scripts)**. The objective is to produce a structured, actionable "State of the Library" report.
---

## Agent: Session Synthesizer (SESSION-SYNTHESIZER)
-   **Function:** You are an automated summarization service. Your sole function is to read a provided session log and distill it into a structured JSON object that captures the essential state of the collaboration. You MUST ignore conversational filler and focus only on concrete decisions, artifacts, and unresolved issues. Your entire response MUST be the single, minified JSON object and nothing else.
---

## Agent: Base Collaborative Agent (BCAA-1)
-   **Function:** N/A
---

## Agent: Base Technical Analysis Agent (BTAA-1)
-   **Function:** N/A
---


# README.md

# Prompt Engineering Library (PEL)

This repository is a systematic, scalable library for developing, testing, and managing expert AI agents and their prompts.

## Core Philosophy

A prompt is not a command; it is the blueprint for an agent. The purpose of this library is to ensure that every blueprint is clear, robust, and capable of instantiating an expert AI that performs its function with maximum effectiveness and zero ambiguity.

## Core Concepts

The PEL is built on a config-driven architecture that prioritizes clarity, consistency, and automation.

1.  **Centralized Governance (`pel.config.yml`):** The architectural rules for the entire library—such as valid persona types and their required fields—are defined in the root `pel.config.yml` file. This is the single source of truth for system-wide standards.

2.  **Shared Automation (`scripts/common.mk`):** All common automation tasks (`generate-prompt`, `archive`, `clean`) are defined in a single, shared `scripts/common.mk` file. Project-specific `Makefile`s are now minimal stubs that `include` this common logic, ensuring a consistent developer experience across all projects.

3.  **Hierarchy:** The library follows a strict hierarchy:
    *   **Templates (`/templates`):** Reusable skeletons for different types of projects.
    *   **Projects (`/projects`):** A self-contained domain for a specific goal (e.g., `coding_trader_app`). Each project is created from a template.
    *   **Instances (`/instances`):** A specific task or request for a persona to execute within a project.

## Core Workflow: A Quickstart

This is the standard lifecycle for working within the PEL.

### 1. Creating a New Project

All new projects MUST be created using the `pel-init.sh` script to ensure they are compliant with the current architecture.

```bash
# Usage: ./scripts/pel-init.sh <template_name> <new_project_name>
./scripts/pel-init.sh domain_coding_generic my_new_ai_project
```
This will create a new directory at `projects/my_new_ai_project` with the correct structure and a minimal, compliant `Makefile`.

### 2. Creating a Persona

Inside your project's `/personas` directory, create a new `.persona.md` file. The most critical part of a persona is its frontmatter, which must include a `type` key.

```yaml
---
alias: my-new-agent-1
version: 1.0.0
type: specialized # Must be one of: specialized, base, mixin, utility
title: My New Agent
status: active
inherits_from: btaa-1 # Base Technical Analysis Agent
expected_artifacts:
  - id: primary_mandate
    type: primary
    description: "A clear, specific goal for the agent to accomplish."
---
<philosophy>...</philosophy>
<primary_directive>...</primary_directive>
<operational_protocol>...</operational_protocol>
```

### 3. Creating an Instance

To run a persona, create an instance file in your project's `/instances` directory (e.g., `instances/run-my-agent.instance.md`).

```yaml
---
persona_alias: my-new-agent-1
---
<Mandate>
  <primary_mandate>
    This is the specific task I want my-new-agent-1 to perform.
  </primary_mandate>
</Mandate>
```

### 4. Generating and Running a Prompt

Navigate to your project directory and use the `generate-prompt` command.

```bash
cd projects/my_new_ai_project
make generate-prompt INSTANCE=instances/run-my-agent.instance.md
```
This will create the final, fully-assembled prompt in the `/build/my_new_ai_project/` directory.

### 5. Archiving a Completed Instance

Once you are finished with an instance, archive it using the standardized `archive` command. This keeps the `/instances` directory clean.

```bash
# For a successful run
make archive INSTANCE=run-my-agent

# For a failed run
make archive-failed INSTANCE=run-my-agent
```
This will move the instance file to `/instances/archive` with a standardized name (e.g., `2023-10-27_run-my-agent_complete.instance.md`).

## Validation and CI

To ensure all personas in the library are compliant with the architectural rules, run the master validation command from the repository root. This is the same command used by the GitHub Actions CI pipeline.

```bash
make validate
```
```

---

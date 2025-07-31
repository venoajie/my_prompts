
---
#### **File to Create: `domains/coding_trader_app/README.md`**
```markdown
# Domain: Coding Trader App

This domain contains all personas, knowledge, and instances related to the development and maintenance of the Python-based algorithmic trading application.

## Purpose

The primary goal of this domain is to leverage AI agents to accelerate development, improve code quality, ensure architectural integrity, and perform complex system analysis.

## Key Personas

This domain provides several key agent types:

*   **Base Personas (`base/`):**
    *   `btaa-1`: Base Technical Analysis Agent (for all technical, fact-based tasks).
    *   `bcaa-1`: Base Collaborative Agent (for all creative or design-oriented tasks).
*   **Specialized Personas (`specialized/`):**
    *   `sia-1`: Systems Integrity Analyst (for debugging production issues).
    *   `bpr-1`: Best Practices Reviewer (for code reviews).
    *   `csa-1`: Collaborative Systems Architect (for designing new features).
    *   ... and many others. Refer to the directory for a full list.
*   **Mixins (`mixins/`):**
    *   `codegen-standards-1`: A non-executable set of rules for code generation, inherited by other personas.

## Knowledge Base

The `knowledge_base/` for this domain contains the ground truth for all operations:
*   `ARCHITECTURE_BLUEPRINT.md`: The canonical system architecture.
*   `src/`: A mirror of the application's source code, used for analysis and refactoring.
```

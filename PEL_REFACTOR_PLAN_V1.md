<!-- DOCUMENT ID: PEL_REFACTOR_PLAN_V1 -->
<!-- TITLE: Implementation Plan: "Templates & Instances" Architectural Refactoring -->
<!-- STATUS: In-Progress -->

### **1.0 Project Mandate & Definition of Done**

*   **Mandate:** To refactor the Prompt Engineering Library (PEL) from a monolithic governance model to a "Templates & Instances" architecture. This will isolate project-specific complexity, improve modularity, and establish a scalable foundation for future growth.
*   **Definition of Done:** The refactoring is complete when a new project can be initialized, customized, and used via the new `pel-init.sh` script and domain-specific `Makefile` without any dependency on logic outside its own project directory or the global `/scripts` and `/engine` directories. The `coding_trader_app` project must be fully functional in its new location.

### **2.0 Current Session State**

*   **Last Update:** `YYYY-MM-DD HH:MM UTC`
*   **Completed Phases:** `[None]`
*   **Current Phase:** `Phase 1: Preparation & Tooling`
*   **Next Action:** `1.1 - Create the 'templates' and 'projects' directories.`

### **3.0 Phased Implementation Plan**

This plan is sequential. Each step must be completed and verified before proceeding to the next. At the end of a session, update the "Status" of the completed step to `[DONE]` and update the "Current Session State" section above.

---

#### **Phase 1: Preparation & Tooling (Current)**

*Goal: Establish the new directory structure and create the necessary automation scripts before moving any project files.*

*   **Step 1.1: Create Core Directories**
    *   **Action:** In the repository root, create two new directories: `/templates` and `/projects`.
    *   **Verification:** The directories `/templates` and `/projects` exist at the root level.
    *   **Status:** `[PENDING]`

*   **Step 1.2: Create the `pel-init.sh` Scaffolding Script**
    *   **Action:** Create a new file at `/scripts/pel-init.sh` with the content provided in the architectural proposal. Make it executable (`chmod +x`).
    *   **Verification:** The script exists and has execute permissions.
    *   **Status:** `[PENDING]`

*   **Step 1.3: Create the Root Dispatcher `Makefile`**
    *   **Action:** Replace the content of the root `Makefile` with the new, simplified dispatcher logic that delegates commands to domain-specific Makefiles using `make -C ...`.
    *   **Verification:** Running `make` at the root displays the new help message. Running `make validate` still functions correctly (it will be updated later).
    *   **Status:** `[PENDING]`

---

#### **Phase 2: Template Creation**

*Goal: Populate the `/templates` directory with the first generic, reusable domain template.*

*   **Step 2.1: Create the Generic Coding Template Directory**
    *   **Action:** Create the directory structure: `/templates/domain_coding_generic/personas/base/`.
    *   **Verification:** The directory path exists.
    *   **Status:** `[PENDING]`

*   **Step 2.2: Relocate Base Personas**
    *   **Action:** **Move** the following files:
        *   `domains/shared/personas/base/btaa-1.persona.md` -> `templates/domain_coding_generic/personas/base/btaa-1.persona.md`
        *   `domains/shared/personas/base/bcaa-1.persona.md` -> `templates/domain_coding_generic/personas/base/bcaa-1.persona.md`
    *   **Verification:** The files are in the new location and the old `/domains/shared` directory can be removed (if empty).
    *   **Status:** `[PENDING]`

*   **Step 2.3: Create Template Artifacts**
    *   **Action:** Create the following two files:
        1.  `/templates/domain_coding_generic/Makefile.template`: Contains only the most generic targets, like `generate-prompt`.
        2.  `/templates/domain_coding_generic/DOMAIN_BLUEPRINT.md.template`: A short, generic blueprint describing a standard coding project architecture.
    *   **Verification:** Both `.template` files exist in the correct location.
    *   **Status:** `[PENDING]`

---

#### **Phase 3: Project Migration (`coding_trader_app`)**

*Goal: Migrate the most complex existing domain into the new `/projects` structure.*

*   **Step 3.1: Relocate the Project Directory**
    *   **Action:** **Move** the entire `/domains/coding_trader_app` directory to `/projects/coding_trader_app`.
    *   **Verification:** The project now resides at `/projects/coding_trader_app`.
    *   **Status:** `[PENDING]`

*   **Step 3.2: Install Project-Specific Governance**
    *   **Action:**
        1.  **Move** the old, complex root `Makefile` to `/projects/coding_trader_app/Makefile`.
        2.  **Move** the old, complex root `PEL_BLUEPRINT.md` to `/projects/coding_trader_app/DOMAIN_BLUEPRINT.md`.
    *   **Verification:** The project now has its own local, complex `Makefile` and `DOMAIN_BLUEPRINT.md`.
    *   **Status:** `[PENDING]`

*   **Step 3.3: Clean Up Redundant Base Personas**
    *   **Action:** The specialized personas within `/projects/coding_trader_app/personas/specialized/` will now inherit from the base personas in the `/templates` directory. Delete any copies of `BTAA-1` or `BCAA-1` from within the project's own `personas` directory if they exist.
    *   **Verification:** The project's `personas` directory contains only specialized agents.
    *   **Status:** `[PENDING]`

---

#### **Phase 4: Tooling & CI/CD Finalization**

*Goal: Update the global scripts to be aware of the new "Templates & Instances" architecture.*

*   **Step 4.1: Update `validate_personas.py`**
    *   **Action:** Replace the content of `/scripts/validate_personas.py` with the "Architecture-Aware" version (v2.0) proposed previously. This version understands `base` vs. `specialized` types.
    *   **Verification:** Run `make validate` from the root. The command should successfully find and validate all personas in their new locations (`/templates` and `/projects`), applying the correct rules to each.
    *   **Status:** `[PENDING]`

*   **Step 4.2: Update `pel_toolkit.py`**
    *   **Action:** Modify the `assemble_persona_content` function (and any other file-finding functions) in `/scripts/pel_toolkit.py`. The script must be updated with a new search path logic:
        1.  Look for inherited personas within the current project's `personas` directory.
        2.  If not found, look within the `personas` directory of the project's corresponding template (as defined in a `.domain_meta` file).
    *   **Verification:** Run `make -C projects/coding_trader_app generate-prompt INSTANCE=...` for a persona that inherits from `BTAA-1`. The assembly must succeed by finding `BTAA-1` in the `/templates` directory.
    *   **Status:** `[PENDING]`

---

#### **Phase 5: Migration of Remaining Domains & Cleanup**

*Goal: Complete the migration for all remaining domains and remove old artifacts.*

*   **Step 5.1: Migrate `prompt_engineering` Domain**
    *   **Action:** Repeat the steps from Phase 3 for the `prompt_engineering` domain. Create its own simple `Makefile` and `DOMAIN_BLUEPRINT.md`. Move `BCCA-1` and `PEL-OC-1` into its `personas` directory.
    *   **Verification:** The `prompt_engineering` project is self-contained in `/projects/prompt_engineering`.
    *   **Status:** `[PENDING]`

*   **Step 5.2: Migrate `language_learning` Domain**
    *   **Action:** Repeat the steps from Phase 3 for the `language_learning` domain.
    *   **Verification:** The `language_learning` project is self-contained in `/projects/language_learning`.
    *   **Status:** `[PENDING]`

*   **Step 5.3: Final Cleanup**
    *   **Action:** Delete the now-empty root `/domains` directory.
    *   **Verification:** The repository structure perfectly matches the target architecture. The entire test suite (if any) passes.
    *   **Status:** `[PENDING]`

---

### **4.0 How to Use This Document**

1.  **Before a Session:** Read the `Current Session State` to understand exactly where you left off.
2.  **During a Session:** Execute the `Next Action` and proceed through the steps of the current phase.
3.  **After a Session:**
    *   For each completed step, change its status from `[PENDING]` to `[DONE]`.
    *   Update the `Current Session State` section at the top of this document with the current date, the list of completed phases, the new current phase, and the next pending action.
    *   Commit this updated file to version control.

This document now acts as a stateful, durable, and comprehensive guide for the entire refactoring process.
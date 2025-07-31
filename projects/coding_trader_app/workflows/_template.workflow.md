
---
#### **File to Create: `domains/coding_trader_app/workflows/README.md`**
```markdown
# Workflows

This directory contains definitions for complex, multi-step tasks that chain together multiple persona instances.

## What is a Workflow?

A workflow is a recipe for achieving a large-scale goal that a single prompt cannot accomplish. It defines a sequence of instances, where the output of one step may become the input for the next.

**Example Goal:** "Add a new endpoint to the API."

This requires:
1.  Designing the API contract (`ADA-1`).
2.  Generating the server-side code (`CSA-1`).
3.  Generating the unit tests (`UTE-1`).
4.  Writing the user documentation (`DCA-1`).

## Workflow Structure

A workflow is defined in a `.workflow.md` file.

**Example: `add_new_endpoint.workflow.md`**
```yaml
---
name: Add New API Endpoint
description: A full end-to-end workflow for designing, implementing, and documenting a new API endpoint.
version: 1.0.0
---

### Step 1: Design the API Contract

**Instance:** `design-new-endpoint.instance.md`
**Persona:** `ADA-1`
**Objective:** Produce a validated OpenAPI specification for the new endpoint.
**Output:** The generated OpenAPI spec, saved to `knowledge_base/api_specs/new_endpoint.yml`.

### Step 2: Implement the Feature

**Instance:** `implement-new-endpoint.instance.md`
**Persona:** `CSA-1`
**Objective:** Generate the server-side code based on the new API spec.
**Input:** `knowledge_base/api_specs/new_endpoint.yml`.

---
<!-- Remainder of workflow definition -->
```
```

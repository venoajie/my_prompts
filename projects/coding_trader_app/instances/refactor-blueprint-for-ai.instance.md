---
domain: prompt_engineering
# FIX: The instance now calls the new, specialized BPA-1 persona.
persona_alias: bpa-1
---

<Mandate>
As the Blueprint Architect, your task is to refactor our `PEL_BLUEPRINT.md` to make it more effective for consumption by both humans and AI agents.

You must use the feedback provided in the injected "Jules Feedback" document as your explicit set of requirements.

Follow your operational protocol. Begin by analyzing both documents and proposing a new structure for the blueprint.
</Mandate>

<h3>Source Document to Refactor:</h3>
<Inject src="PEL_BLUEPRINT.md" />

<h3>Refactoring Requirements:</h3>
<Inject src="knowledge_base/jules_feedback_on_blueprint.md" />
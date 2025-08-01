<Mandate>

    <CanonicalDocuments>
        <!-- Global System Governance -->
        <Inject src="PEL_BLUEPRINT.md" />
        <Inject src="README.md" />

        <!-- `engine` Project Governance -->
        <Inject src="v1/system_kernel.xml" />

        <!-- `scripts` Project Governance -->
        <Inject src="scripts/validate_personas.py" />
        <Inject src="scripts/pel_toolkit.py" />
        <Inject src="scripts/kb_updater.py" />
        <Inject src="scripts/pel-init.sh" />

        <!-- `coding_trader_app` Project Governance -->
        <Inject src="projects/coding_trader_app/Makefile" />
        <Inject src="projects/coding_trader_app/DOMAIN_BLUEPRINT.md" />
        <Inject src="projects/coding_trader_app/AGENTS.md" />
        <Inject src="projects/coding_trader_app/knowledge_base/system_contracts.yml" />
        <Inject src="projects/coding_trader_app/personas/specialized-->various personas" />

        <!-- `prompt_engineering` Project Governance -->
        <Inject src="projects/prompt_engineering/knowledge_base/current_structure.txt" />
        <Inject src="projects/prompt_engineering/knowledge_base/error_report_from_github.md" />

        <!-- `templates` Project Governance -->
        <Inject src="templates/domain_coding_generic/personas/base/btaa-1.persona.md" />
        <Inject src="templates/domain_coding_generic/personas/mixins/codegen-standards-1.mixin.md" />

        <!-- `github` Ci/CD -->
        <Inject src=".github/workflows/validate_pel.yml" />

    </CanonicalDocuments>
</KnowledgeBase>
---
domain: coding_trader_app
persona_alias: jia-1
---
<Mandate>
Take the provided set of new and updated configuration files and generate a single, schema-validated `JULES_MANIFEST.json`. The manifest should consist of a series of `CREATE_FILE` or `UPDATE_FILE` operations to apply these changes to the `trading-app` repository.
</Mandate>

<Evidence>
    <Artifact name="Implementation Artifacts from CSA-1">
        <Description>The full output from the CSA-1 persona in Phase 1, containing the final content for all files.</Description>
        <Content>
            <!-- Paste the full output from the CSA-1 session here -->
        </Content>
    </Artifact>
    <Artifact name="Jules Manifest Schema">
        <Description>The schema for validating the output.</Description>
        <Inject src="domains/prompt_engineering/knowledge_base/jules_manifest.schema.json" />
    </Artifact>
</Evidence>
---
domain: coding_trader_app
persona_alias: dca-1
target_repo_path: ../trading-app
---
<Mandate>
The trading application has been refactored to support separate development and production configurations using a `docker-compose.yml` base file and `docker-compose.dev.yml`/`docker-compose.prod.yml` overrides.

Your task is to update the `README.md` file to reflect this new workflow. The documentation should clearly explain how to start the application in each environment using the new `make dev-up` and `make prod-up` commands.
</Mandate>

<Evidence>
    <Artifact name="New Makefile">
        <Description>The updated Makefile with the new targets.</Description>
        <Inject src="Makefile" />
    </Artifact>
    <Artifact name="Existing README">
        <Description>The README.md file to be updated.</Description>
        <Inject src="README.md" />
    </Artifact>
</Evidence>
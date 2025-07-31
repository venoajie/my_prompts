---
domain: coding_trader_app
persona_alias: csa-1
target_repo_path: ../trading-app
---
<Mandate>
Your task is to take the provided A1.Flex optimization recommendations and generate a complete set of new and modified configuration artifacts for the trading application.

The final output must be a structured response containing the complete, final content for all of the following files:
1.  A new base `docker-compose.yml`.
2.  A new `docker-compose.dev.yml` override file.
3.  A new `docker-compose.prod.yml` override file.
4.  A new `config/redis.prod.conf` file.
5.  A new `config/postgresql.prod.conf` file.
6.  A new `scripts/optimize-system.sh` file.
7.  An updated `Makefile` that includes the new `dev-up`, `prod-up`, and `deploy` targets.
8.  A new `/etc/docker/daemon.json` file.
</Mandate>

<Evidence>
    <Artifact name="Optimization Recommendations">
        <Description>The full text of the optimization recommendations to be implemented.</Description>
        <Content>
            <!-- Paste the full text of the recommendations here -->
        </Content>
    </Artifact>
    <Artifact name="Current Docker Compose">
        <Description>The existing docker-compose.yml to be refactored.</Description>
        <Inject src="docker-compose.yml" />
    </Artifact>
    <Artifact name="Current Makefile">
        <Description>The existing Makefile to be updated.</Description>
        <Inject src="Makefile" />
    </Artifact>
</Evidence>
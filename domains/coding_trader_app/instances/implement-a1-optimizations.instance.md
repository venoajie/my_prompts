---
domain: coding_trader_app
persona_alias: csa-1
---

<Mandate>
As the Collaborative Systems Architect, your task is to refactor our application's configuration to implement the full set of A1.Flex optimizations and multi-environment best practices provided below.

Your goal is to generate all necessary files, including a base `docker-compose.yml`, environment-specific overrides (`.dev.yml`, `.prod.yml`), all `.conf` files, the `daemon.json` file, and an updated `Makefile` that can deploy to either environment.

Follow your operational protocol. Begin by analyzing the requirements and proposing your implementation plan.
</Mandate>

<h3>Optimization and Multi-Environment Requirements:</h3>
<Inject src="knowledge_base/a1_flex_optimization_plan.md" />
# Project Roadmap: "MY TRADING APP"
_Last Updated: 2025-07-18_

## Phase 1: Pipeline Hardening (Q4 2025)

-   `[STATUS: IN_PROGRESS]` **Dynamic Subscription Control:** Implement the utility for interacting with the `Receiver`'s Redis control channel.
-   `[STATUS: TODO]` **Automated Data Pruning:** Implement the database maintenance tasks.
-   `[STATUS: COMPLETE]` **Canonical Instrument Model:** Resolved all cross-service data consistency bugs.
-   `[STATUS: COMPLETE]` End-to-End Bug Fixes: Resolved cascading startup failures across all services. The root cause was a combination of infrastructure misconfiguration (Redis protected mode) and application-level technical debt (legacy global singletons). The system now starts reliably.

### Current Iteration Goal (Sprint ending 2025-07-20)
The focus is on validating and hardening the end-to-end data pipeline with multiple exchanges.

### Backlog & Status

#### Critical Path
-   **[CRITICAL-NEXT]** **Full System Test:** Perform an end-to-end test of the complete, multi-exchange data pipeline. Verify that data flows correctly from `receiver` -> `distributor` -> `PostgreSQL` and that the `backfill` service correctly processes its queued work.
-   **[NEXT]** **Dynamic Subscription Control:** Implement and test the command-line utility for interacting with the `Receiver`'s Redis control channel to dynamically subscribe/unsubscribe from Binance streams.
-   **[NEXT]** **Automated Data Pruning:** Implement the database maintenance tasks for automatically expiring `public_trades` data and trimming `ohlc` data according to configured retention policies.

#### Completed Work
-   **[COMPLETE]** **System Startup Stabilization:** Refactored `executor` and `receiver` to use dependency injection, hardened the `janitor` startup logic, and corrected the Docker Compose configuration to ensure a reliable, sequential startup.
-   **[COMPLETE]** **Canonical Instrument Model:** Resolved all cross-service data consistency bugs.
-   **[COMPLETE]** **Multi-Market Binance Integration:** `Janitor` service is fully capable of fetching data from all Binance markets.
-   **[COMPLETE]** **Layered & Scalable Configuration:** Refactored config system to be fully DRY.
-   **[COMPLETE]** **Analyzer/Executor Integration:** Implemented a Redis Pub/Sub channel (`channel:system_events`) for inter-service communication. The `analyzer` now publishes volume anomaly alerts, and the `executor` subscribes to these events for notifications and has been refactored to use Binance OHLC data as its primary analysis source.
-   [STATUS: COMPLETE] **Full System Test & Pipeline Hardening:** Performed an end-to-end test of the complete data pipeline. Resolved critical bugs in the `janitor` bootstrap, `distributor` OHLC aggregation, and `backfill` worker lifecycle to ensure a reliable data flow from ingestion to persistence.
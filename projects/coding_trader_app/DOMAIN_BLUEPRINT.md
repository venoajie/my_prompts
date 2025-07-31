# PROJECT_BLUEPRINT_V2.5.md
<!-- PROJECT BLUEPRINT: "MY TRADING APP" -->
<!-- Version: 2.5 -->
<!-- CHANGE LOG: Refactored for machine-first readability and clarity. -->

# 1. System Overview
This system is a high-throughput, low-latency data pipeline designed to ingest, process, and persist real-time and historical market data from multiple cryptocurrency exchanges. Its primary function is to provide a reliable, ordered, and queryable data foundation for algorithmic trading strategies.

The architecture is service-oriented, containerized via Docker, and orchestrated by Docker Compose. A strict dependency injection pattern is enforced for all database clients. A canonical data model provides a consistent, exchange-agnostic representation of all market data.

**Core Documentation:**
*   **This Document (The Constitution):** Describes the "What" and the "Why" of the system architecture.
*   **/AGENTS.md (The Operator's Manual):** Describes the "How" – providing the exact commands for testing, linting, and dependency management.
*   **/docs/system_contracts.yml (The Data Dictionary):** Provides the definitive, machine-readable schema for all data contracts (Redis streams, queues, etc.).

# 2. Core Principles & Data Flow
(This section remains conceptually the same but with paths updated)

### 2.1. Canonical Data Model
All exchange-specific data is transformed into a standard internal format. The canonical source for these data structures is defined in `/docs/system_contracts.yml`.

### 2.2. State-Driven Operation
The operational mode for each exchange is governed by a central state machine in Redis.
*   **State Key:** `system:state:<exchange>` (e.g., `system:state:deribit`)
*   **States:** `BOOTSTRAPPING`, `RECONCILING`, `HEALTHY`, `LOCKED`, `AUDITING`

### 2.3. Startup Sequence & Orchestration
Docker Compose enforces a strict startup order. The `/janitor` service runs first to synchronize instruments and set the initial system state. All other long-running services depend on its successful completion.

# 3. Service Directory

---
### Service: `analyzer`
- **Role:** Performs real-time analysis on the market data stream.
- **Source Location:** `/src/services/analyzer/`
- **Interacts With:**
    - **Writes To:** Log files, Redis Pub/Sub (`channel:system_events`).
    - **Reads From:** Redis Stream (`stream:market_data`), PostgreSQL (`v_instruments`).
---
### Service: `backfill`
- **Role:** Performs historical data backfilling.
- **Source Location:** `/src/services/backfill/`
- **Interacts With:**
    - **Writes To:** PostgreSQL (`ohlc`).
    - **Reads From:** Redis (`queue:ohlc_work`), Exchange REST APIs, PostgreSQL (`instruments`).
---
### Service: `distributor`
- **Role:** Persists canonical real-time data to PostgreSQL.
- **Source Location:** `/src/services/distributor/`
- **Interacts With:**
    - **Writes To:** PostgreSQL (`public_trades`, `ohlc`, `tickers`).
    - **Reads From:** Redis Stream (`stream:market_data`).
---
### Service: `executor`
- **Role:** Executes automated trading strategies.
- **Source Location:** `/src/services/executor/`
- **Interacts With:**
    - **Writes To:** Deribit REST API, PostgreSQL (`orders`).
    - **Reads From:** PostgreSQL (`orders`, `v_instruments`, `ohlc`), Redis (`system:state:simple`, `ticker:*`, `channel:system_events`).
---
### Service: `janitor`
- **Role:** System governor and bootstrap orchestrator.
- **Source Location:** `/src/services/janitor/`
- **Interacts With:**
    - **Writes To:** PostgreSQL (`instruments`), Redis (`system:state:<exchange>`, `queue:ohlc_work`).
    - **Reads From:** Exchange REST APIs, PostgreSQL (`instruments`).
---
### Service: `maintenance`
- **Role:** Provides on-demand database cleanup utilities.
- **Source Location:** `/src/scripts/maintenance/`
- **Interacts With:** PostgreSQL (`instruments`).
---
### Service: `receiver`
- **Role:** Ingests real-time market data via WebSocket.
- **Source Location:** `/src/services/receiver/`
- **Interacts With:**
    - **Writes To:** Redis Stream (`stream:market_data`), Redis Hash (`ticker:*`).
    - **Reads From:** Exchange WebSocket APIs, Redis Pub/Sub (`control:<market_id>:subscriptions`).
---

# 4. Data & State Contracts
**Note:** The authoritative source for these contracts is the machine-readable file located at `/docs/system_contracts.yml`. The following is a human-readable summary.

*   **Market Data Stream:** Redis Stream `stream:market_data`
*   **OHLC Backfill Queue:** Redis List `queue:ohlc_work`
*   **System Event Channel:** Redis Pub/Sub `channel:system_events`
*   **Canonical Instrument Model:** PostgreSQL Table `instruments`

# 5. Operational Runbooks
**Note:** These runbooks provide context. The exact commands are maintained in `/AGENTS.md`.

## 5.1. How to Manually Unlock the System
**Use Case:** The system is in the `LOCKED` state after a bootstrap.
1.  **Verify Data:** Query the database to ensure bootstrap integrity.
2.  **Execute Unlock:** Run the `system_unlock.py` script.
3.  **Confirm State:** Check the Redis state key.

## 5.2. How to Dynamically Manage Binance Subscriptions
**Use Case:** Add or remove a real-time trade stream without a restart.
1.  **Connect to Redis:** Access the Redis CLI.
2.  **Publish Command:** Publish a formatted JSON command to the `control:binance_spot:subscriptions` channel.

# 6. Known Failure Modes & Recovery Strategies
(This section remains conceptually the same)
# 6. Known Failure Modes & Recovery Strategies

- **Failure Mode:** `distributor` consumers repeatedly crash or log "Moving to DLQ stream".
  - **Likely Cause:** A "poison pill" message in the `stream:market_data` stream with a schema that fails validation in the `distributor`. This could be due to a bug in a `receiver` client's transformation logic.
  - **Recovery:**
    1.  Inspect the Dead Letter Queue (DLQ) for the failed messages: `XREAD COUNT 10 STREAMS dlq:stream:market_data 0-0`.
    2.  Analyze the `payload` of the failed message to identify the schema error.
    3.  Identify and fix the bug in the responsible `receiver` client that produced the malformed message.
    4.  Deploy the fix. The `distributor` will then be able to process new, valid messages.
    5.  Manually decide whether to discard the messages in the DLQ (`XTRIM`) or attempt to repair and re-inject them.

- **Failure Mode:** `executor` logs "Persistent Position Mismatch" alerts and the `ReconciliationAgent` repeatedly triggers self-repair audits that fail.
  - **Likely Cause:**
      1. A bug in the `janitor`'s `run_historical_audit_for_exchange` task prevents it from finding/inserting missing trades.
      2. The exchange API is returning incomplete or erroneous transaction log data.
      3. A fundamental flaw in the `AccountState` manager's position calculation logic.
  - **Recovery:**
    1.  Lock the system manually by setting the Redis state to `LOCKED` to prevent further trading.
    2.  Examine the logs for both the `executor` and `janitor` services to find the root cause of the audit failure.
    3.  Manually compare the `orders` table in PostgreSQL with the exchange's trade history UI to find the discrepancy.
    4.  Once the root cause is fixed (e.g., code fix, manual DB entry), run the `system_unlock.py` script.

- **Failure Mode:** Services fail to write to Redis, logging `ConnectionError` or `ResponseError` related to memory.
  - **Likely Cause:** The Redis instance has hit its `maxmemory` limit, and the `noeviction` policy is correctly rejecting new writes.
  - **Recovery:**
    1.  **Short-term:** Increase the `mem_limit` for the `redis` service in `docker-compose.yml` and restart the stack.
    2.  **Long-term:** Implement the "Automated Data Pruning" task from the project roadmap. This involves creating a maintenance script that periodically runs `XTRIM` on Redis streams and expires old keys to keep memory usage in check.

- **Failure Mode:** `analyzer` service repeatedly crashes or logs errors related to a specific symbol.
  - **Likely Cause:** A malformed message for a specific symbol is causing a parsing or calculation error in the analysis logic. The in-memory state for that symbol might be corrupted.
  - **Recovery:**
    1.  Examine the `analyzer` logs to identify the problematic symbol and the error.
    2.  If possible, use the dynamic subscription control channel to temporarily unsubscribe from the problematic symbol's stream to stabilize the system.
    3.  Fix the bug in the `analyzer`'s processing logic.
    4.  Deploy the fix and restart the `analyzer` service. It will rebuild its in-memory state from the live data stream.

# 7. Known Limitations & Future Improvements

## 7.1. Database Schema Management
- **Current State:** The database schema is defined and initialized by the `/init.sql` script. This script is executed by the Postgres container only on first run with an empty data volume. This approach is suitable for development but is not viable for production.
- **Future Requirement:** For production deployment, a formal database migration tool (e.g., Alembic, Flyway, or a custom versioned script runner) must be implemented. This will allow for applying incremental, non-destructive schema changes to a live database without data loss. This is a required work item before the system can be considered production-ready.

## 4.0 Jules Integration Strategy

This project utilizes the Jules agent for delegated execution tasks, governed by the principles in the root `PEL_BLUEPRINT.md`. The integration is governed by the following critical principles:

*   **Principle: Commit-Locked Execution:** To ensure determinism, all interactions with Jules MUST be locked to a specific Git commit hash. The `pel_toolkit.py` script automatically gathers the current `HEAD` commit hash and injects it into a `<SystemContext>` block at the start of every prompt. The Jules-facing personas (`JIA-1`, `JTA-1`) are responsible for parsing this context and instructing Jules to `git checkout` this specific hash before performing any operations.

*   **Principle: Dual-Mode Interaction:** The integration operates in two distinct, mutually exclusive modes to ensure maximum effectiveness and safety.

    1.  **Mode A: Manifest-Based Execution (Deterministic Tasks):** For pre-approved, deterministic changes. This is the **preferred mode for safety and reliability.**
        *   **Trigger:** The human operator uses the `JIA-1` persona.
        *   **Input:** An implementation plan, generated code artifacts, and the current commit hash (injected by the toolchain).
        *   **Output:** A `JULES_MANIFEST.json` file that includes the `commit_hash`, and a guided prompt instructing Jules to check out that hash before executing the manifest.

    2.  **Mode B: Guided Task Generation (Exploratory Tasks):** For generative or exploratory tasks.
        *   **Trigger:** The human operator uses the `JTA-1` persona.
        *   **Input:** A high-level goal, key context files, and the current commit hash (injected by the toolchain).
        *   **Output:** A guided, natural-language prompt that instructs Jules to first check out the specified commit hash before proceeding with the task.
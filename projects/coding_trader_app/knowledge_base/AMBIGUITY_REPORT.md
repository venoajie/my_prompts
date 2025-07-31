# AMBIGUITY_REPORT.md

<!-- AMBIGUITY REPORT: "MY TRADING APP PROJECT" -->
---

1.  **[RESOLVED] Critical `Receiver` Bug:** The `receiver/main.py` was instantiating WebSocket clients with incompatible constructor signatures. **Fix:** The `DeribitWsClient` and `BinanceWsClient` `__init__` methods were refactored to a standard signature accepting `market_definition`, `redis_client`, and `postgres_client` arguments, aligning them with a dependency injection pattern.

2.  **[RESOLVED] Legacy Singleton Dependencies:** Multiple services (`executor`, `receiver`) relied on importing global singleton instances of database clients (e.g., `from core.db.postgres import postgres_client`), which were removed to prevent startup deadlocks. This caused `ImportError` crashes. **Fix:** The affected services were refactored to use a dependency injection pattern. The main entrypoint for each service now creates the client instances and passes them to the necessary classes during initialization.

3.  **[RESOLVED] Bootstrap Logic Duplication:** The `janitor`'s `run_historical_audit_for_exchange(full_bootstrap=True)` is the modern, integrated way to perform a historical trade backfill. The legacy script `src/scripts/maintenance/initial_bootstrap.py` had overlapping functionality and caused conflicts during startup. **Fix:** The legacy bootstrap script has been deprecated and removed from the system's startup sequence. The `janitor` service is now the single, authoritative source for all bootstrap operations, including instrument syncing and OHLC work queuing.

4.  **Inconsistent System State Handling:** The system uses two patterns for state: per-exchange (e.g., `system:state:deribit`) and global (`system:state:simple`). The `executor` reads the global state, which could lead to it trading on a healthy exchange while another is `LOCKED`. The interaction and priority between these states must be clarified.

5.  **`Executor` Multi-Exchange Path:** The `executor` service is currently hardcoded for Deribit. The architectural path to supporting trading on other exchanges (like Binance) is not defined. It is unclear if the plan is to create a separate `executor-binance` service or to refactor the current `executor` into a generic host.
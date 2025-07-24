<Instance>
    <KnowledgeBase>
        <!-- CORE ARCHITECTURE -->
        <Document id="ARCHITECTURE_BLUEPRINT" version="2.5" src="PROJECT_BLUEPRINT_V2.5.md" description="The primary architectural blueprint and single source of truth."/>
        <RawDataSource id="DOCKER_COMPOSE_CONFIG" path="docker-compose.yml" description="The Docker Compose file defining the system's services and startup sequence."/>

        <!-- KEY ARTIFACTS FOR TESTING -->
        <Document id="DERIBIT_WS_CLIENT_PY_SOURCE" src="src/services/receiver/exchange_clients/deribit_ws_client.py" description="The Deribit client to be validated for the race condition fix."/>
        <Document id="ANALYZER_MAIN_PY_SOURCE" src="src/services/analyzer/main.py" description="The service responsible for detecting volume anomalies."/>
        <Document id="STRATEGY_ENGINE_PY_SOURCE" src="src/services/executor/deribit/strategy_engine.py" description="The service component that will be activated by the state change."/>
        <Document id="SYSTEM_UNLOCK_PY_SOURCE" src="src/scripts/maintenance/system_unlock.py" description="The script used to transition the system from LOCKED to HEALTHY."/>
    </KnowledgeBase> 
    <SessionState>    
        <last_outcome status="SUCCESS">
            <summary>Successfully hardened and validated the end-to-end data pipeline. A series of critical bugs were resolved across the janitor, distributor, and backfill services. The system is now in a stable state where data correctly flows from ingestion through persistence, and both real-time and historical data pipelines are confirmed to be functional.</summary>
            <system_status>STABLE</system_status>
            <data_pipeline_status>HEALTHY</data_pipeline_status>
        </last_outcome>
    </SessionState>

    <Runtime>
        <ActivatePersona alias="SIA-1"/>
        <Mandate>
            <Objective id="VALIDATE_INCOMPLETE_FIXES">
                <Description>Deploy and validate the pending fix for the `deribit_ws_client` startup race condition.</Description>
                <Task id="TASK-1">Confirm that after a clean startup, the `receiver` service successfully subscribes to Deribit instrument channels without warnings.</Task>
            </Objective>
            <Objective id="TEST_ANALYSIS_AND_NOTIFICATION_LOGIC">
                <Description>Perform an end-to-end test of the `analyzer`'s alert-to-notification workflow.</Description>
                <Task id="TASK-2">Create a new Python test script (`src/scripts/tests/inject_volume_spike.py`) that connects to Redis and injects a series of `aggTrade` messages into the `stream:market_data` stream, simulating a large volume spike for `BTCUSDT`.</Task>
                <Task id="TASK-3">Execute the test script and verify that a corresponding "VOLUME_ANOMALY_DETECTED" alert is received via the Telegram notification system.</Task>
            </Objective>
            <Objective id="TEST_EXECUTOR_ROBUSTNESS">
                <Description>Perform a basic functional test of the `executor`'s trading logic.</Description>
                <Task id="TASK-4">Execute the `system_unlock.py` script to transition the system state from `LOCKED` to `HEALTHY`.</Task>
                <Task id="TASK-5">Monitor the `executor` logs to confirm that the `StrategyEngine` begins its evaluation loop and attempts to place trades based on the (now available) Deribit market data.</Task>
            </Objective>
            <Objective id="VALIDATE_SUCCESS">
                <Description>Define the explicit success criteria for this test plan.</Description>
                <Validation id="V-1" for_task="TASK-1">
                    <Artifact>Logs for the `receiver` service.</Artifact>
                    <ExpectedOutcome>The logs must contain the message "Successfully loaded instruments for subscription" and must NOT contain the warning "Instrument list is empty".</ExpectedOutcome>
                </Validation>
                <Validation id="V-2" for_task="TASK-3">
                    <Artifact>External Telegram Client.</Artifact>
                    <ExpectedOutcome>A notification containing the text "VOLUME ANOMALY DETECTED" and details about the BTCUSDT volume spike must be received.</ExpectedOutcome>
                </Validation>
                <Validation id="V-3" for_task="TASK-5">
                    <Artifact>Logs for the `executor` service.</Artifact>
                    <ExpectedOutcome>The logs must contain the message "System state is 'HEALTHY'" and "Starting strategy engine evaluation loop", and must NOT contain the warning "Pausing new strategy execution".</ExpectedOutcome>
                </Validation>
            </Objective>
        </Mandate>
    </Runtime>
</Instance>

That is an excellent and critical question. The prompt I prepared will validate the *functional correctness* of the core application logic—the "happy path." It will confirm that if A happens, B and C correctly follow.

However, that is **not all**.

A truly robust, production-ready application requires testing beyond the happy path. The tests we have planned are crucial, but they represent the next logical step, not the final one.

Here is a breakdown of the other relevant tests that should be performed as the application matures, categorized by domain:

### 1. `Executor` and Strategy Logic Testing (Highest Priority Next)

The current test only confirms the `executor` *starts*. It does not validate its complex trading logic.

*   **State Reconciliation Test:** Manually place a trade on the Deribit testnet exchange that the application doesn't know about.
    *   **Goal:** Verify that the `ReconciliationAgent` detects this "ghost" order on its next cycle and takes the correct remedial action (e.g., cancelling it or flagging it for review), as described in its logic.
*   **Position Mismatch Test:** Manually alter a position size in the PostgreSQL `orders` table to create a discrepancy with the exchange.
    *   **Goal:** Verify that the `ReconciliationAgent` detects the position mismatch, triggers the `CRITICAL` alert, and initiates the self-repair audit (`_run_historical_audit_for_currency`), as documented in the blueprint's failure modes.
*   **Strategy Logic Validation:** This is the most complex. It involves creating a controlled market data environment (either by replaying historical data or injecting specific ticker prices) to test specific strategy triggers.
    *   **Goal:** Verify that if you inject a price that crosses a take-profit threshold for an open position, the `StrategyEngine` correctly generates a `CREATE_ORDER` command to close the position.

### 2. Failure and Recovery Testing ("Chaos Engineering Lite")

These tests validate the system's resilience and adherence to the documented recovery strategies.

*   **Redis Failure:** Temporarily stop the `redis` container while the system is running.
    *   **Goal:** Verify that services like the `receiver`, `distributor`, and `executor` enter a retry loop with appropriate error logging, and that they successfully reconnect and resume normal operation once Redis is brought back online, without data loss.
*   **PostgreSQL Failure:** Temporarily stop the `postgres` container.
    *   **Goal:** Verify that services that depend on the database pause their operations gracefully and recover when the database is restored.
*   **"Poison Pill" Message Injection:** Manually inject a malformed message (e.g., a trade with a non-numeric price) into the `stream:market_data` Redis stream.
    *   **Goal:** Verify that the `distributor`'s main processing loop does not crash. The message should be correctly moved to the Dead Letter Queue (`dlq:stream:market_data`), and a corresponding error should be logged, exactly as described in the blueprint's failure modes.
*   **Service Crash Simulation:** Manually kill the `distributor` or `backfill` container mid-operation.
    *   **Goal:** For the `distributor`, verify that upon restart, the `recover_stale_messages` task correctly reclaims and processes any messages that were left unacknowledged. For the `backfill` service, verify that it correctly picks up the task it was working on without creating duplicate data.

### 3. Performance and Stress Testing

These tests determine the operational limits of the system.

*   **High-Frequency Data Injection:** Modify the volume spike injection script to push a sustained, high-frequency stream of trades (e.g., 1000 trades/second) for several minutes.
    *   **Goal:** Monitor the CPU and memory usage of the `receiver`, `redis`, and `distributor` services. Measure the end-to-end latency to ensure it does not degrade unacceptably under load.
*   **Database Connection Pool Exhaustion:** Write a test script that opens a large number of simultaneous connections to the PostgreSQL database.
    *   **Goal:** Verify that the application services handle connection timeouts gracefully and recover, rather than crashing.

### **Recommendation and Path Forward**

The test plan I generated for you is the correct and necessary **next step**. It validates the core application logic, which is the highest priority after establishing data pipeline stability.

Once that test plan is successfully completed, I would recommend creating a new testing phase on the roadmap focused on the items above, likely in this order of priority:

1.  **`Executor` and Strategy Logic Testing:** This is the highest business value, as it validates the core trading functionality.
2.  **Failure and Recovery Testing:** This is critical for building confidence in the system's production-readiness.
3.  **Performance and Stress Testing:** This is important for understanding scaling limits and identifying bottlenecks before they become production issues.
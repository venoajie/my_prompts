<!-- PEL INSTANCE REQUEST: 001 -->
<!-- SYSTEM CORE: PEL_SYSTEM_CORE_V1.0.prompt -->
<Instance>
    <KnowledgeBase>
        <!-- De-duplicated and cleaned list of documents -->
        <Document id="ARCHITECTURE_BLUEPRINT" version="2.5" src="PROJECT_BLUEPRINT_V2.5.md" description="The primary architectural blueprint and single source of truth."/>
        <Document id="AMBIGUITY_REPORT" version="1.0" src="AMBIGUITY_REPORT.md" description="Identifies known bugs and logical inconsistencies."/>
        <Document id="PROJECT_ROADMAP" version="1.1" src="PROJECT_ROADMAP.md" description="Outlines project phases and priorities."/>
        <Document id="DERIBIT_WS_CLIENT_PY_SOURCE" src="src/services/receiver/exchange_clients/deribit_ws_client.py" version="1.0" description="WebSocket client for Deribit. Essential for validating the fix for the startup race condition."/>
        <Document id="ANALYZER_MAIN_PY_SOURCE" src="src/services/analyzer/main.py" version="1.0" description="Entrypoint for the analyzer service. Required to understand the anomaly detection logic."/>
        <Document id="SYSTEM_UNLOCK_PY_SOURCE" src="src/scripts/maintenance/system_unlock.py" version="1.0" description="Transitions the system from LOCKED to HEALTHY state."/>
        <Document id="NOTIFICATION_MANAGER_PY_SOURCE" src="src/shared/notifications/manager.py" version="1.0" description="Manages Telegram notifications for system alerts."/>
        <Document id="RAW_DOCKER_COMPOSE" src="docker-compose.yml" description="Docker Compose configuration defining the system's services."/>
        <!-- Other necessary documents from the original list would be included here -->
    </KnowledgeBase> 
    <SessionState>    
        <last_outcome status="SUCCESS">
            <summary>The session successfully hardened and validated the end-to-end data pipeline. The system is now in a stable state where data correctly flows from ingestion through persistence. A known, non-critical race condition in the `deribit_ws_client` was identified, and a code fix was developed but has not yet been deployed and validated.</summary>
            <system_status>STABLE</system_status>
            <data_pipeline_status>HEALTHY</data_pipeline_status>
        </last_outcome>
    </SessionState>
    <Runtime>
        <ActivatePersona alias="TAE-1"/>
        <Mandate>
            <TestPlan id="TP-01" name="System Logic and Robustness Validation">
                <Description>Validate the application's logical correctness and robustness under simulated real-world conditions now that the data pipeline is stable.</Description>
                <TestCase id="TC-01" name="Deribit Client Startup Fix Validation">
                    <Objective>Confirm that after a clean startup, the `receiver` service successfully subscribes to Deribit instrument channels without warnings.</Objective>
                    <Action>Perform a clean system startup using the provided `RAW_DOCKER_COMPOSE`.</Action>
                    <Verification>Monitor the `receiver` service logs for successful subscription messages and the absence of race condition warnings related to `deribit_ws_client`.</Verification>
                    <ExpectedResult>The `receiver` log shows successful subscription to all configured Deribit channels without errors.</ExpectedResult>
                </TestCase>
                <TestCase id="TC-02" name="Alert-to-Notification Workflow Test">
                    <Objective>Perform an end-to-end test of the `analyzer`'s alert-to-notification workflow.</Objective>
                    <Action id="ACTION-2.1">Generate a new Python script (`inject_volume_spike.py`) that connects to Redis and injects a series of `aggTrade` messages into the `stream:market_data` stream, simulating a large volume spike for `BTCUSDT`.</Action>
                    <Action id="ACTION-2.2">Execute the generated script.</Action>
                    <Verification>Confirm that a "VOLUME_ANOMALY_DETECTED" alert is published to the `channel:system_events` Redis channel and that a corresponding Telegram notification is sent by the notification manager.</Verification>
                    <ExpectedResult>A Telegram message is received containing the details of the volume anomaly alert.</ExpectedResult>
                </TestCase>
                <TestCase id="TC-03" name="Executor Functional Test">
                    <Objective>Perform a basic functional test of the `executor`'s trading logic.</Objective>
                    <Action id="ACTION-3.1">Execute the `system_unlock.py` script to transition the system state from `LOCKED` to `HEALTHY`.</Action>
                    <Verification>Monitor the `executor` logs.</Verification>
                    <ExpectedResult>The `executor` logs show that the `StrategyEngine` has started its evaluation loop and is processing market data.</ExpectedResult>
                </TestCase>
            </TestPlan>
        </Mandate>
    </Runtime>
</Instance>
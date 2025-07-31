### `README.md` 

# Trading Application Deployment and Operations Guide

This document provides the authoritative instructions for deploying, managing, and operating the multi-service trading application.

## System Architecture Overview

The application is a service-oriented, high-throughput data pipeline designed for ingesting, processing, and analyzing market data from multiple cryptocurrency exchanges (initially Deribit and Binance).

*   **`janitor` (System Governor):** A critical one-shot service that runs on every startup. It synchronizes instrument definitions, performs historical data backfills, and sets the initial operational state for each exchange.
*   **`receiver` (Producer):** Connects to exchange WebSockets, ingests real-time market data, and publishes it to the Redis message bus.
*   **`redis` (Message Broker):** Acts as a durable, in-memory message queue that decouples data ingestion from processing.
*   **`distributor` (Consumer/Persister):** Reads canonical messages from the Redis Stream and performs bulk inserts into the PostgreSQL database.
*   **`analyzer` (Consumer/Analyst):** Reads from the same Redis Stream in parallel to perform real-time analysis, such as volume anomaly detection.
*   **`postgres` (Database):** The final, persistent data store for all trade, order, and OHLC data.
*   **`executor` (Decision Engine):** A state-aware service that executes trading strategies and manages orders, governed by the system's health state.
*   **`backfill` / `maintenance` (Utility Services):** On-demand, one-shot services for running large-scale historical data ingestion and database cleanup tasks.

This decoupled architecture ensures that a failure or restart of one service does not cause a cascading failure of the entire system.

## 1. Prerequisites

*   Docker and Docker Compose are installed and running.
*   You have active API credentials for the exchanges you intend to use.
*   `git` is installed to clone the repository.

## 2. Initial Setup and Deployment

These steps are performed once to initialize the system. The first launch is a special **Bootstrap Phase** that requires manual sign-off before automated trading can begin.

### Step 2.1: Create Secret Files

The application uses Docker Secrets to manage sensitive credentials. Create a `secrets` directory in the project root and populate it with the following files.

**Never commit the `secrets` directory to version control.**

```bash
# Create the directory
mkdir -p secrets

# 1. Create Deribit API secrets (if using Deribit)
echo "YOUR_DERIBIT_CLIENT_ID" > secrets/deribit_client_id.txt
echo "YOUR_DERIBIT_CLIENT_SECRET" > secrets/deribit_client_secret.txt

# 2. Create the PostgreSQL Database Password
echo "YOUR_SECURE_DATABASE_PASSWORD" > secrets/db_password.txt

# 3. (Optional) Create Telegram secrets for error notifications
echo "YOUR_TELEGRAM_BOT_TOKEN" > secrets/telegram_bot_token.txt
echo "YOUR_TELEGRAM_CHAT_ID" > secrets/telegram_chat_id.txt

# 4. Set secure permissions for the secret files
chmod 600 secrets/*.txt
```

### Step 2.2: Configure the Application

Key operational parameters are managed in `src/shared/config/strategies.toml`. Before the first launch, review and configure:
*   **`[[public_symbols]]`**: The list of symbols to monitor and backfill.
*   **`[backfill]`**: The `start_date` for historical data ingestion.
*   **`[analyzer]`**: Parameters for the real-time anomaly detection service.

### Step 2.3: First-Time Launch (Bootstrap & Backfill)

The first launch will trigger the `janitor` to bootstrap the system and the `backfill` service to ingest historical public trades.

```bash
# This command builds all images and starts all services defined in the 'full' and 'backfill' profiles.
# The janitor will run first, then the backfill and other services will start.
docker-compose --profile full --profile backfill up --build -d
```

**What Happens During First Launch:**
1.  The `janitor` service starts, connects to all configured exchanges, syncs the `instruments` table, and performs an OHLC backfill. It then sets the system state for each exchange to `LOCKED`.
2.  The `backfill` service starts and begins downloading historical public trade data from Binance's data repository.
3.  The `receiver`, `distributor`, and `analyzer` services start and begin processing real-time data.
4.  The `executor` starts but will remain in a safe, non-trading mode until the system is manually unlocked.

You can monitor the progress of all services with `docker-compose logs -f`.

### Step 2.4: Manual Verification and System Unlock (Critical)

After the `janitor` and `backfill` services have completed, you must manually verify the system's state and then authorize it to begin trading.

1.  **Verify Data:** Connect to the database and ensure the tables are populated as expected.
    ```bash
    # Connect to the database
    docker-compose exec postgres psql -U trading_app -d trading

    # Example queries:
    SELECT exchange, market_type, count(*) FROM instruments GROUP BY 1, 2;
    SELECT count(*) FROM public_trades;
    SELECT count(*) FROM ohlc WHERE tick > now() - interval '1 day';
    ```

2.  **Run the Unlock Script:** Execute the provided maintenance script to unlock the system. This signals that you have verified the initial state and approve the start of automated trading.
    ```bash
    # This command runs the unlock script inside a temporary container
    docker-compose run --rm janitor python src/scripts/maintenance/system_unlock.py
    ```
    After running this script, the system will transition to a `HEALTHY` state, and the `executor` will begin normal operations.

## 3. Daily Operations and Management

### Viewing Logs
```bash
# View logs for all running services in real-time
docker-compose logs -f

# View logs for a specific service (e.g., the executor)
docker-compose logs -f executor
```

### Checking Service Status
```bash
docker-compose ps
```

### Stopping and Starting the Full Application
```bash
# To Stop All Services:
docker-compose down

# To Start All Services (after initial setup):
docker-compose --profile full up -d
```

### Running Maintenance Tasks
The `maintenance` profile is used for database cleanup.
```bash
# This runs both the trade and instrument pruning jobs in the correct order
docker-compose --profile maintenance up --build
```

## 4. Troubleshooting

### CRITICAL: System Clock Inaccuracy

The application includes a "Time Sanity Check" that runs when each service starts. It compares the server's clock against reliable world time servers. If the clock is off by more than 60 seconds, the service will refuse to start with a `CRITICAL TIME SKEW DETECTED` error.

**This is a critical safety feature.** A trading system cannot operate safely with an incorrect clock.

**Diagnosis:**
1.  Log into the host machine (`opc@instance...`).
2.  Run the `date` command. If it shows a date in the future or far in the past, the clock is wrong.

**Solution:**
The host machine's Network Time Protocol (NTP) service is likely misconfigured or not running.
1.  Ensure the `chrony` package is installed: `sudo dnf install chrony`
2.  Enable and start the `chrony` service: `sudo systemctl enable --now chronyd`
3.  Verify it is syncing: `chronyc sources`. The `^*` indicates the currently synced source.
4.  Once `date` shows the correct time, perform a full, clean restart of the application to ensure all containers inherit the correct time:
    ```bash
    docker-compose down -v
    docker-compose --profile full up --build -d
    ```

### System Cleanup (Destructive)

**WARNING:** These commands will permanently delete all stored data. The next launch will require a full bootstrap and backfill procedure.

```bash
# Stop all services and remove containers, networks, and data volumes
docker-compose down -v

# To aggressively prune all unused Docker assets (images, build cache)
docker system prune -a -f
```

```bash
# Stop all services and remove all associated data volumes
docker system prune -a -f
docker rm -f $(docker ps -aq)
docker volume rm trading-app_pgdata
docker compose --profile full up --build --force-recreate

```

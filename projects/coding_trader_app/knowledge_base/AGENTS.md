# AGENTS.md

# Agent Operator's Manual for "My Trading App"
<!-- Version: 2.3 -->
<!-- CHANGE LOG: Replaced incorrect Alembic reference with accurate init.sql workflow. -->

This file provides explicit, executable commands and instructions for any AI agent or developer interacting with this repository. This is the **Single Source of Truth** for operational commands.

## 1. Core Principles for Agents
- **Idempotency:** All scripts and commands should be designed to be safely re-runnable.
- **Explicitness:** Do not infer commands or paths. Use the exact commands provided herein.
- **Verification:** After any `write` operation, perform a `read` operation to confirm the change was successful.

## 2. Environment & Sanity Checks
Before running any other command, ensure the environment is correctly configured.

```bash
# Verify Docker is running and responsive
docker ps

# Check out the main branch and ensure it is up to date
git checkout main
git pull origin main
```

## 3. Running the Application
The application services are managed using Docker Compose and are organized into profiles. This allows for running the entire stack or individual services.

> **Note on Syntax:** This manual uses the modern `docker compose` (v2) command syntax, which is standard in current Docker installations, including those on Oracle Linux 9. If you are using a legacy system with an older version, you may need to use `docker-compose` (with a hyphen).

**To run the complete application stack:**
This command starts all services defined in the `full` profile in detached mode.
```bash
docker compose --profile full up -d
```

**To run a specific service and its dependencies:**
You can start a single service by specifying its profile name.
```bash
# Example: Start only the 'receiver' service and its core dependencies (redis, postgres)
docker compose --profile receiver up -d
```

**To view logs:**
Follow the logs for a specific service or for the entire stack.
```bash
# Follow logs for a single service (e.g., receiver)
docker compose logs -f receiver

# Follow logs for all running services
docker compose logs -f
```

**To stop the application:**
This command stops and removes all containers and networks created by `up`.
```bash
docker compose down
```

## 4. Quality & Testing Commands
All changes MUST pass the following checks before being submitted.

```bash
# Run all linters and formatters
docker compose run --rm lint

# Run all unit and integration tests
docker compose run --rm test
```

## 5. Dependency Management
Dependencies are managed via `pyproject.toml` files and installed using `uv` during the Docker image build process. No Python dependencies need to be installed on the host machine.

There are two types of dependency files:
1.  **Shared Dependencies:** A central file at `/src/shared/pyproject.toml` manages libraries used by multiple services.
2.  **Service-Specific Dependencies:** Each service has its own file (e.g., `/src/services/receiver/pyproject.toml`) for libraries unique to that service.

**To add or update a dependency:**
1.  Identify the correct `pyproject.toml` file to edit.
2.  From the repository root, rebuild the Docker image for the affected service(s).

    ```bash
    # Example: Rebuild the 'receiver' service image after editing its dependencies
    docker compose build receiver
    ```

## 6. Database Management
The database schema is defined entirely within the `/init.sql` file. This file is automatically executed by the Postgres container only on its first startup when the database volume is empty.

**Initial Setup:**
The schema is created automatically when you first run `docker compose up`. No manual steps are needed.

**Making Schema Changes (Development Only):**
The current process for applying schema changes is to completely reset the database. **WARNING: This will destroy all existing data.**

1.  Modify the `/init.sql` file with your desired schema changes (e.g., `ALTER TABLE`, `CREATE TABLE`).
2.  Stop and remove all containers, **including the database volume**. The `-v` flag is critical.
    ```bash
    docker compose down -v
    ```
3.  Restart the application. The Postgres container will detect the empty volume and re-run the updated `/init.sql` script.
    ```bash
    docker compose --profile full up -d
    ```

> **Note:** A formal, non-destructive database migration strategy for production environments is a known requirement. See `/PROJECT_BLUEPRINT_V2.5.md` for details.

## 7. Key Documentation Artifacts
An agent's effectiveness depends on understanding the correct roles of these documents.

- **/PROJECT_BLUEPRINT_V3.0.md:** The **System Constitution.** Read this to understand architecture, data flows, and design principles.
- **/AGENTS.md (This File):** The **Operator's Manual.** Use this file for the exact commands needed to test, build, and maintain the repository.
- **/docs/system_contracts.yml:** The **Data Dictionary.** Refer to this for the canonical, machine-readable schemas of all data contracts.
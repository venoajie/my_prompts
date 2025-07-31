### Analysis & Plan

This plan implements the A1.Flex optimization recommendations by refactoring the monolithic Docker Compose file into a more robust and environment-agnostic structure. This approach enhances maintainability, security, and performance, particularly for production deployments.

**1. Docker Compose Refactoring (Base + Overrides):**
*   The single `docker-compose.yml` has been split into three files to separate common definitions from environment-specific settings.
*   **`docker-compose.yml` (Base):** This file now contains only the core service definitions, network configurations, and secrets, which are common across all environments. Environment-specific details like ports, volumes, resource limits, and restart policies have been removed. [REASONED_INFERENCE based on `Directive_CodeAsConfig`, `Current Docker Compose`]
*   **`docker-compose.dev.yml` (Development):** This override file is for local development. It exposes service ports (`6380:6379`, `5432:5432`) for direct access and debugging. It uses standard named volumes for data persistence during development sessions. [REASONED_INFERENCE based on common development practices]
*   **`docker-compose.prod.yml` (Production):** This override file is hardened for production. It does not expose any ports to the host, uses specific volume mounts defined in the `Makefile` (`/data/volumes/...`), and enforces strict memory limits and reservations. It also mounts external configuration files for Redis and PostgreSQL and sets `restart: unless-stopped` policies for service reliability. [REASONED_INFERENCE based on `Current Docker Compose`, `Current Makefile`]

**2. Externalized Production Configurations:**
*   To avoid embedding configuration inside the Docker Compose file, production settings for Redis and PostgreSQL have been moved to dedicated `.conf` files. This aligns with best practices for managing production systems. [Source: `Directive_CodeAsConfig:NoMagicValues`]
*   **`config/redis.prod.conf`:** Contains the memory and networking settings previously defined as command-line arguments.
*   **`config/postgresql.prod.conf`:** Contains the connection and performance tuning parameters for the database, optimized for a production environment.

**3. System-Level Optimizations:**
*   **`scripts/optimize-system.sh`:** A new script to apply critical kernel-level `sysctl` settings for improving network throughput and memory management, which are essential for a high-performance trading application.
*   **`/etc/docker/daemon.json`:** A configuration file for the Docker daemon itself. It relocates Docker's data directory to the dedicated block volume (`/data/docker`) and configures log rotation to prevent unbounded log growth from consuming all disk space. [REASONED_INFERENCE based on `Current Makefile`]

**4. Build System Integration (`Makefile`):**
*   The `Makefile` has been updated with new, clear targets for managing the different environments:
    *   `dev-up`: Starts the system using the `development` overrides.
    *   `prod-up`: Starts the system using the `production` overrides.
    *   `deploy`: A new top-level target that runs the system optimization script and then launches the production stack. This serves as the primary command for deploying the application.

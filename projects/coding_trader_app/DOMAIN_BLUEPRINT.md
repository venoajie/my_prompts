# projects\coding_trader_app\DOMAIN_BLUEPRINT.md

# DOMAIN_BLUEPRINT.md
# Project: Coding Trader App

**Version:** 1.0
**Status:** Active
**Template:** domain_coding_generic

## 1.0 Project Overview

This document outlines the architectural principles and core components for the **Coding Trader App** project. This project is a Python-based application designed for algorithmic trading on cryptocurrency exchanges. It is managed within the Prompt Engineering Library (PEL).

This blueprint is the "Single Source of Truth" for all architectural decisions within this project.

## 2.0 Core Principles

This project adheres to the global principles defined in the root `PEL_BLUEPRINT.md` and adds the following project-specific constraints:

*   **Principle 2.1 (Technology Stack):** The application is built using Python 3.11, with `FastAPI` for the web interface, `SQLAlchemy` for ORM, and `PostgreSQL` as the primary data store. All services are containerized with Docker.
*   **Principle 2.2 (Testing Strategy):** All new business logic MUST be accompanied by unit tests using the `pytest` framework. Integration tests will be used to validate interactions between services and the database.
*   **Principle 2.3 (Code Style):** All Python code MUST adhere to the `black` code formatter and `flake8` for linting.
*   **Principle 2.4 (Immutability):** All data transfer objects (DTOs) and data models passed between services should be treated as immutable. Pydantic models with `frozen=True` are preferred.

## 3.0 Key Components & Services

This section describes the high-level components of the trading application.

*   **Service: `market-data-ingestor`**
    *   **Responsibility:** Connects to the Deribit exchange via WebSocket to stream and store real-time market data (trades, order books) into the PostgreSQL database.
    *   **Key Dependencies:** `PostgreSQL`, `Deribit API`.

*   **Service: `strategy-executor`**
    *   **Responsibility:** Reads market data, applies defined trading strategies (e.g., momentum, mean-reversion), and generates trade signals.
    *   **Key Dependencies:** `PostgreSQL`, `market-data-ingestor`.

*   **Service: `order-manager`**
    *   **Responsibility:** Receives trade signals from the `strategy-executor`, places orders on the exchange via REST API, and tracks their lifecycle (open, filled, cancelled).
    *   **Key Dependencies:** `Deribit API`, `PostgreSQL`.

*   **Service: `reconciliation-agent`**
    *   **Responsibility:** Periodically compares the state of orders and positions in the local database with the state reported by the exchange to detect and flag discrepancies.
    *   **Key Dependencies:** `Deribit API`, `PostgreSQL`.

*   **Shared Library: `shared-models`**
    *   **Responsibility:** Contains all Pydantic and SQLAlchemy data models used across the services to ensure consistency.
    *   **Key Dependencies:** None.

## 4.0 Jules Integration Strategy

This project utilizes the Jules agent for delegated execution tasks, governed by the principles in the root `PEL_BLUEPRINT.md`.

*   **Mode A (Manifest-Based):** Used for deterministic tasks like deploying new code, applying database migrations, or updating configurations. The `JIA-1` persona is the designated architect for these manifests.
*   **Mode B (Guided Task):** Used for generative tasks like creating new documentation, writing a new API client, or refactoring a class. The `JTA-1` persona is the designated architect for these tasks.
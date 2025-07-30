# docker-compose.yml (Base Configuration)
# Contains common definitions for all environments.
version: '3.9'

services:
  redis:
    image: redis/redis-stack:7.2.0-v7
    profiles:  ["full", "receiver", "distributor", "janitor", "executor", "backfill", "analyzer"]
    networks: [trading-net]
    healthcheck:
      test: ["CMD-SHELL", "redis-cli PING | grep PONG"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 20s

  postgres:
    image: postgres:17
    profiles:  ["full", "receiver", "distributor", "janitor", "executor", "backfill", "analyzer"]
    environment:
      POSTGRES_USER: trading_app
      POSTGRES_DB: trading
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    secrets: [db_password]
    networks: [trading-net]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U trading_app -d trading"]
      interval: 10s
      timeout: 5s
      retries: 5

  janitor:
    profiles: ["full", "janitor"]
    build:
      context: .
      dockerfile: src/services/janitor/Dockerfile
      args:
        - BUILDPLATFORM=linux/arm64
    env_file: ./.env
    environment:
      - SERVICE_NAME=janitor
      - REDIS_URL=redis://redis:6379
      - POSTGRES_HOST=postgres
      - POSTGRES_USER=trading_app
      - POSTGRES_DB=trading
    secrets:
      - db_password
      - source: deribit_client_id
        target: deribit_client_id
      - source: deribit_client_secret
        target: deribit_client_secret
    depends_on:
      redis: { condition: service_healthy }
      postgres: { condition: service_healthy }
    networks: [trading-net]

  analyzer:
    profiles: ["full", "analyzer"]
    build:
      context: .
      dockerfile: src/services/analyzer/Dockerfile
      args:
        - BUILDPLATFORM=linux/arm64
    env_file: ./.env
    environment:
      - SERVICE_NAME=analyzer
      - REDIS_URL=redis://redis:6379
      - POSTGRES_HOST=postgres
      - POSTGRES_USER=trading_app
      - POSTGRES_DB=trading
    secrets: [db_password]
    depends_on:
      janitor: { condition: service_completed_successfully }
    networks: [trading-net]

  backfill:
    profiles: ["full", "backfill"]
    build:
      context: .
      dockerfile: src/services/backfill/Dockerfile
      args:
        - BUILDPLATFORM=linux/arm64
    env_file: ./.env
    environment:
      - SERVICE_NAME=backfill
      - REDIS_URL=redis://redis:6379
      - POSTGRES_HOST=postgres
      - POSTGRES_USER=trading_app
      - POSTGRES_DB=trading
    secrets: [db_password]
    depends_on:
      janitor: { condition: service_completed_successfully }
    networks: [trading-net]

  distributor:
    profiles: ["full", "distributor"]
    build:
      context: .
      dockerfile: src/services/distributor/Dockerfile
      args:
        - BUILDPLATFORM=linux/arm64
    env_file: ./.env
    environment:
      - SERVICE_NAME=distributor
      - REDIS_URL=redis://redis:6379
      - POSTGRES_HOST=postgres
      - POSTGRES_USER=trading_app
      - POSTGRES_DB=trading
    secrets: [db_password]
    depends_on:
      janitor: { condition: service_completed_successfully }
    networks: [trading-net]

  executor:
    profiles: ["full", "executor"]
    build:
      context: .
      dockerfile: src/services/executor/Dockerfile
      args:
        - BUILDPLATFORM=linux/arm64
    env_file: ./.env
    environment:
      - SERVICE_NAME=executor
      - REDIS_URL=redis://redis:6379
      - POSTGRES_HOST=postgres
      - POSTGRES_USER=trading_app
      - POSTGRES_DB=trading
    secrets:
      - db_password
      - source: deribit_client_id
        target: deribit_client_id
      - source: deribit_client_secret
        target: deribit_client_secret
    depends_on:
      janitor: { condition: service_completed_successfully }
    networks: [trading-net]

  receiver:
    profiles: ["full", "receiver"]
    build:
      context: .
      dockerfile: src/services/receiver/Dockerfile
      args:
        - BUILDPLATFORM=linux/arm64
    env_file: ./.env
    environment:
      - SERVICE_NAME=receiver
      - REDIS_URL=redis://redis:6379
      - POSTGRES_HOST=postgres
      - POSTGRES_USER=trading_app
      - POSTGRES_DB=trading
    secrets:
      - db_password
      - source: deribit_client_id
        target: deribit_client_id
      - source: deribit_client_secret
        target: deribit_client_secret
    depends_on:
      janitor: { condition: service_completed_successfully }
    networks: [trading-net]

volumes:
  redis-data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/volumes/redis-data
  pgdata:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /data/volumes/pgdata

secrets:
  db_password:
    file: ./secrets/db_password.txt
  deribit_client_id:
    file: ./secrets/client_id.txt
  deribit_client_secret:
    file: ./secrets/client_secret.txt

networks:
  trading-net:
    driver: bridge
    driver_opts:
      com.docker.network.bridge.name: trading-br
    ipam:
      config:
        - subnet: 172.20.0.0/16

# docker-compose.dev.yml
# docker-compose.dev.yml (Development Overrides)
# Use with: docker compose -f docker-compose.yml -f docker-compose.dev.yml up
version: '3.9'

services:
  redis:
    ports: ["6380:6379", "8001:8001"]
    command:
      - redis-server
      - "--bind 0.0.0.0"
      - "--protected-mode no"
    mem_limit: 800m
    mem_reservation: 600m

  postgres:
    ports: ["5432:5432"]
    # For development, use a simple password instead of secrets
    environment:
      POSTGRES_PASSWORD: "devpassword"
    # Secrets block must be cleared to prevent compose from looking for the file
    secrets: []
    command:
      - "-c"
      - "max_connections=50" # Lower for dev
    mem_limit: 800m
    mem_reservation: 512m

  janitor:
    environment: { POSTGRES_PASSWORD: "devpassword" }
    secrets: []
    restart: on-failure
    mem_limit: 200m
    mem_reservation: 100m

  analyzer:
    environment: { POSTGRES_PASSWORD: "devpassword" }
    secrets: []
    restart: on-failure
    mem_limit: 256m
    mem_reservation: 128m

  backfill:
    environment: { POSTGRES_PASSWORD: "devpassword" }
    secrets: []
    restart: on-failure
    mem_limit: 256m
    mem_reservation: 128m

  distributor:
    environment: { POSTGRES_PASSWORD: "devpassword" }
    secrets: []
    restart: on-failure
    mem_limit: 384m
    mem_reservation: 256m

  executor:
    environment: { POSTGRES_PASSWORD: "devpassword" }
    secrets: []
    restart: on-failure
    mem_limit: 256m
    mem_reservation: 128m

  receiver:
    environment: { POSTGRES_PASSWORD: "devpassword" }
    secrets: []
    restart: on-failure
    mem_limit: 384m
    mem_reservation: 256m


# docker-compose.prod.yml
    # docker-compose.prod.yml (Production Overrides & Optimizations)
# Use with: docker compose -f docker-compose.yml -f docker-compose.prod.yml up
version: '3.9'

services:
  redis:
    volumes:
      - redis-data:/data
      - ./config/redis.prod.conf:/usr/local/etc/redis/redis.conf:ro
    command: redis-server /usr/local/etc/redis/redis.conf
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 800m
          cpus: '0.5'
        reservations:
          memory: 600m
          cpus: '0.25'
    sysctls:
      - net.core.somaxconn=65535
    ulimits:
      memlock:
        soft: -1
        hard: -1

  postgres:
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
      POSTGRES_INITDB_ARGS: "--encoding=UTF8 --data-checksums"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
      - ./config/postgresql.prod.conf:/etc/postgresql/postgresql.conf:ro
    command: postgres -c config_file=/etc/postgresql/postgresql.conf
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1g
          cpus: '1.0'
        reservations:
          memory: 768m
          cpus: '0.5'
    shm_size: 256m

  janitor:
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/db_password }
    restart: on-failure
    deploy:
      resources:
        limits: { memory: 200m, cpus: '0.2' }
        reservations: { memory: 100m, cpus: '0.1' }

  analyzer:
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/db_password }
    restart: unless-stopped
    deploy:
      resources:
        limits: { memory: 256m, cpus: '0.25' }
        reservations: { memory: 128m, cpus: '0.1' }

  backfill:
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/db_password }
    restart: unless-stopped
    deploy:
      resources:
        limits: { memory: 256m, cpus: '0.25' }
        reservations: { memory: 128m, cpus: '0.1' }

  distributor:
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/db_password }
    restart: unless-stopped
    deploy:
      resources:
        limits: { memory: 384m, cpus: '0.4' }
        reservations: { memory: 256m, cpus: '0.2' }

  executor:
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/db_password }
    restart: unless-stopped
    deploy:
      resources:
        limits: { memory: 256m, cpus: '0.25' }
        reservations: { memory: 128m, cpus: '0.1' }

  receiver:
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/db_password }
    restart: unless-stopped
    deploy:
      resources:
        limits: { memory: 384m, cpus: '0.4' }
        reservations: { memory: 256m, cpus: '0.2' }

# config/redis.prod.conf
        # Redis configuration optimized for A1.Flex
bind 0.0.0.0
protected-mode no
port 6379

# Memory
maxmemory 600mb
maxmemory-policy noeviction

# Persistence
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes

# Performance
io-threads 2
io-threads-do-reads yes

# Disable huge pages warning
disable-thp yes

# ARM-specific
activerehashing yes
hz 10

# Logging
loglevel notice
logfile ""

# config/postgresql.prod.conf
# PostgreSQL optimized for A1.Flex with 18GB RAM
# General Settings
listen_addresses = '*'
max_connections = 100
jit = off # Aligned with application client setting

# Memory (for ~1GB allocated to PG)
shared_buffers = 256MB
effective_cache_size = 768MB
work_mem = 4MB
maintenance_work_mem = 64MB

# Storage/Checkpoint
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
max_worker_processes = 3
max_parallel_workers_per_gather = 1
max_parallel_workers = 2

# Logging
log_destination = 'stderr'
logging_collector = off
log_min_duration_statement = 1000
log_timezone = 'UTC'

# ARM optimization
huge_pages = off

# scripts/optimize-system.sh
#!/bin/bash
# System optimizations for A1.Flex trading system

echo "Applying system-level optimizations for trading workload..."

# Increase file descriptors
echo "Updating file descriptor limits in /etc/security/limits.conf..."
sudo tee -a /etc/security/limits.conf > /dev/null << EOF
* soft nofile 65535
* hard nofile 65535
EOF

# Kernel parameters for trading/database workload
echo "Updating kernel parameters in /etc/sysctl.conf..."
sudo tee -a /etc/sysctl.conf > /dev/null << EOF

# Network optimizations for high-throughput trading
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr
net.core.default_qdisc = fq

# Memory optimizations
vm.swappiness = 10
vm.dirty_ratio = 15
vm.dirty_background_ratio = 5
vm.overcommit_memory = 1

# File system limits
fs.file-max = 2097152
fs.inotify.max_user_watches = 524288
EOF

echo "Applying new kernel parameters..."
sudo sysctl -p

# Setup swap on block volume (useful for memory spikes)
if [ -f "/data/swapfile" ]; then
    echo "Swapfile already exists. Skipping creation."
else
    echo "Creating 4GB swapfile on /data/swapfile..."
    sudo dd if=/dev/zero of=/data/swapfile bs=1G count=4
    sudo chmod 600 /data/swapfile
    sudo mkswap /data/swapfile
    sudo swapon /data/swapfile
    echo "/data/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
fi

echo "✓ System optimization complete."

# Makefile
# =====================================================================
# Universal Makefile for OCI Block Volume Setup + Trading System Deploy
# =====================================================================
# Works on: Oracle Linux 9, Ubuntu 24, Ubuntu 22.04
# Purpose: Automate block volume setup and trading system deployment
# Author: Trading System DevOps
# =====================================================================

# OS Detection and Environment Setup
OS_NAME := $(shell grep '^ID=' /etc/os-release | cut -d'=' -f2 | tr -d '"')
OS_VERSION := $(shell grep '^VERSION_ID=' /etc/os-release | cut -d'=' -f2 | tr -d '"')
HOSTNAME := $(shell hostname)
TIMESTAMP := $(shell date +%Y%m%d-%H%M%S)

# OS-specific Configuration
ifeq ($(OS_NAME),ol)
    # Oracle Linux settings
    DEFAULT_USER = opc
    DEFAULT_GROUP = opc
    SUDO_GROUP = wheel
    SELINUX_ENABLED = true
    PACKAGE_MANAGER = dnf
else ifeq ($(OS_NAME),ubuntu)
    # Ubuntu settings
    DEFAULT_USER = ubuntu
    DEFAULT_GROUP = ubuntu
    SUDO_GROUP = sudo
    SELINUX_ENABLED = false
    PACKAGE_MANAGER = apt-get
else
    # Generic Linux settings
    DEFAULT_USER = $(shell whoami)
    DEFAULT_GROUP = $(shell whoami)
    SUDO_GROUP = sudo
    SELINUX_ENABLED = false
    PACKAGE_MANAGER = apt-get
endif

# Block Volume Configuration Variables
MOUNT_POINT = /data
VOLUME_OWNER = $(DEFAULT_USER):$(DEFAULT_GROUP)
FILESYSTEM_TYPE = ext4
DOCKER_DATA_DIR = $(MOUNT_POINT)/docker
TRADING_APP_DIR = $(MOUNT_POINT)/trading-app
BACKUP_DIR = $(MOUNT_POINT)/backups

# Auto-detected Block Device Variables
DEVICE := $(shell lsblk -rno NAME,TYPE | grep disk | grep -v -E 'sda|vda' | awk '{print "/dev/"$$1}' | head -1)
PARTITION := $(DEVICE)1
UUID := $(shell sudo blkid $(PARTITION) 2>/dev/null | grep -o 'UUID="[^"]*"' | cut -d'"' -f2)

# Trading System Configuration
TRADING_REPO_URL = https://github.com/your-org/trading-system.git
TRADING_BRANCH = main
CURRENCY_TO_BOOTSTRAP = BTC
COMPOSE_BASE_FILE = docker-compose.yml
COMPOSE_DEV_OVERRIDE = docker-compose.dev.yml
COMPOSE_PROD_OVERRIDE = docker-compose.prod.yml

# ANSI Color codes for pretty output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
BLUE = \033[0;34m
MAGENTA = \033[0;35m
CYAN = \033[0;36m
WHITE = \033[1;37m
NC = \033[0m # No Color

# Default target when just running 'make'
.DEFAULT_GOAL := help

# =======================
# HELP AND DOCUMENTATION
# =======================
.PHONY: help
help:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "$(WHITE)   OCI Block Volume + Trading System Setup Makefile$(NC)"
	@echo "$(BLUE)================================================================$(NC)"
	@echo ""
	@echo "$(CYAN)System Information:$(NC)"
	@echo "  OS Detected    : $(GREEN)$(OS_NAME) $(OS_VERSION)$(NC)"
	@echo "  Hostname       : $(GREEN)$(HOSTNAME)$(NC)"
	@echo "  Default User   : $(GREEN)$(DEFAULT_USER)$(NC)"
	@echo "  Block Device   : $(GREEN)$(or $(DEVICE),NOT FOUND - Attach volume first!)$(NC)"
	@echo "  Mount Point    : $(GREEN)$(MOUNT_POINT)$(NC)"
	@echo ""
	@echo "$(CYAN)Quick Start Commands:$(NC)"
	@echo "  $(GREEN)make complete-setup$(NC)     - Run full setup (volume + trading system)"
	@echo "  $(GREEN)make volume-setup$(NC)       - Setup block volume only"
	@echo "  $(GREEN)make trading-setup$(NC)      - Setup trading system only"
	@echo ""
	@echo "$(MAGENTA)TRADING SYSTEM COMMANDS (ENVIRONMENT-AWARE)$(NC)"
	@echo "  $(GREEN)make deploy$(NC)             - Smart deploy (detects prod/dev from hostname)"
	@echo "  $(GREEN)make dev-up$(NC)              - Start development environment"
	@echo "  $(GREEN)make dev-down$(NC)            - Stop development environment"
	@echo "  $(GREEN)make prod-up$(NC)             - Start production environment"
	@echo "  $(GREEN)make prod-down$(NC)           - Stop production environment"
	@echo ""
	@echo "$(CYAN)Block Volume Commands:$(NC)"
	@echo "  $(GREEN)make check$(NC)              - Check current disk status"
	@echo "  $(GREEN)make setup$(NC)              - Create partition on block device"
	@echo "  $(GREEN)make format$(NC)             - Format the volume ($(RED)DESTROYS DATA!$(NC))"
	@echo ""
	@echo "$(CYAN)Trading System Commands (Legacy):$(NC)"
	@echo "  $(GREEN)make install-docker$(NC)     - Install Docker and Docker Compose"
	@echo "  $(GREEN)make trading-deploy$(NC)     - Deploy trading application (legacy)"
	@echo ""
	@echo "$(YELLOW)For detailed help on any command, run: make help-<command>$(NC)"
	@echo "$(BLUE)================================================================$(NC)"

# =======================
# COMPLETE SETUP TARGETS
# =======================
.PHONY: complete-setup volume-setup trading-setup

complete-setup:
	@echo "$(BLUE)================================================================$(NC)"
	@echo "$(WHITE)         Complete OCI Instance Setup Starting...$(NC)"
	@echo "$(BLUE)================================================================$(NC)"
	@$(MAKE) volume-setup
	@echo ""
	@$(MAKE) install-docker
	@echo ""
	@$(MAKE) trading-setup
	@echo ""
	@echo "$(GREEN)✓ Complete setup finished successfully!$(NC)"
	@echo "$(YELLOW)Next step: run 'make deploy' to start the application.$(NC)"

volume-setup: check setup format mount permanent selinux-fix test create-directories
	@echo "$(GREEN)✓ Block volume setup complete!$(NC)"

trading-setup: check-docker trading-deploy
	@echo "$(GREEN)✓ Trading system setup complete!$(NC)"

# =======================================
# TRADING SYSTEM COMMANDS (ENVIRONMENT-AWARE)
# =======================================
.PHONY: deploy dev-up dev-down prod-up prod-down

deploy:
	@echo "$(YELLOW)=== Smart Deploying Application ===$(NC)"
	@if echo "$(HOSTNAME)" | grep -qiE "prod|prd"; then \
		echo "$(MAGENTA)Production hostname detected. Deploying production stack...$(NC)"; \
		$(MAKE) prod-up; \
	else \
		echo "$(CYAN)Development hostname detected. Deploying development stack...$(NC)"; \
		$(MAKE) dev-up; \
	fi

dev-up:
	@echo "$(CYAN)Starting development environment...$(NC)"
	docker compose -f $(COMPOSE_BASE_FILE) -f $(COMPOSE_DEV_OVERRIDE) up -d --remove-orphans

dev-down:
	@echo "$(CYAN)Stopping development environment...$(NC)"
	docker compose -f $(COMPOSE_BASE_FILE) -f $(COMPOSE_DEV_OVERRIDE) down

prod-up:
	@echo "$(MAGENTA)Starting PRODUCTION environment...$(NC)"
	docker compose -f $(COMPOSE_BASE_FILE) -f $(COMPOSE_PROD_OVERRIDE) up -d --remove-orphans

prod-down:
	@echo "$(MAGENTA)Stopping PRODUCTION environment...$(NC)"
	docker compose -f $(COMPOSE_BASE_FILE) -f $(COMPOSE_PROD_OVERRIDE) down

# =======================
# BLOCK VOLUME OPERATIONS
# =======================

.PHONY: check
check:
	@echo "$(YELLOW)=== Checking System Status ===$(NC)"
	@echo "$(CYAN)Available block devices:$(NC)"
	@lsblk -f
	@echo ""
	@echo "$(CYAN)Current disk usage:$(NC)"
	@df -h | grep -E "^/dev|^Filesystem" | grep -v tmpfs
	@echo ""
	@if [ -z "$(DEVICE)" ]; then \
		echo "$(RED)ERROR: No additional block device found!$(NC)"; \
		echo "$(YELLOW)Please attach a block volume in OCI Console first.$(NC)"; \
		echo ""; \
		echo "$(CYAN)Detected devices:$(NC)"; \
		lsblk -d -o NAME,SIZE,TYPE,MOUNTPOINT | grep -v loop; \
		exit 1; \
	else \
		echo "$(GREEN)✓ Found device: $(DEVICE)$(NC)"; \
		echo "$(CYAN)Device details:$(NC)"; \
		sudo fdisk -l $(DEVICE) 2>/dev/null | grep -E "^Disk|^Device"; \
	fi

.PHONY: setup
setup: check
	@echo "$(YELLOW)=== Setting up Block Volume ===$(NC)"
	@echo "$(CYAN)This will prepare $(GREEN)$(DEVICE)$(NC) for use as a data volume$(NC)"
	@echo ""
	@if [ -e $(PARTITION) ]; then \
		echo "$(YELLOW)⚠ Partition $(PARTITION) already exists$(NC)"; \
		echo "$(CYAN)Current partition table:$(NC)"; \
		sudo fdisk -l $(DEVICE) | grep ^$(DEVICE); \
	else \
		echo "$(RED)WARNING: This will create a new partition table on $(DEVICE)!$(NC)"; \
		echo "$(YELLOW)All data on this device will be lost!$(NC)"; \
		read -p "Are you sure you want to continue? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1; \
		echo ""; \
		echo "$(CYAN)Creating partition...$(NC)"; \
		echo -e "n\np\n1\n\n\nw" | sudo fdisk $(DEVICE) > /dev/null 2>&1 || \
			(echo -e "g\nn\n1\n\n\nw" | sudo fdisk $(DEVICE) > /dev/null 2>&1); \
		sleep 2; \
		sudo partprobe $(DEVICE) 2>/dev/null || true; \
		echo "$(GREEN)✓ Partition created successfully$(NC)"; \
		echo "$(CYAN)New partition table:$(NC)"; \
		sudo fdisk -l $(DEVICE) | grep ^$(DEVICE); \
	fi

.PHONY: format
format: check
	@echo "$(YELLOW)=== Formatting Block Volume ===$(NC)"
	@if [ -e $(PARTITION) ]; then \
		if sudo blkid $(PARTITION) > /dev/null 2>&1; then \
			echo "$(YELLOW)⚠ WARNING: $(PARTITION) already contains a filesystem!$(NC)"; \
			echo "$(CYAN)Current filesystem info:$(NC)"; \
			sudo blkid $(PARTITION); \
			echo ""; \
			echo "$(RED)ALL DATA ON THIS PARTITION WILL BE PERMANENTLY DELETED!$(NC)"; \
			read -p "Are you absolutely sure you want to format? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ] || exit 1; \
		fi; \
		echo ""; \
		echo "$(CYAN)Formatting $(PARTITION) as $(FILESYSTEM_TYPE)...$(NC)"; \
		sudo mkfs.$(FILESYSTEM_TYPE) -F -L "OCI-DATA" $(PARTITION); \
		sync; \
		echo "$(GREEN)✓ Formatted successfully$(NC)"; \
		echo "$(CYAN)New filesystem info:$(NC)"; \
		sudo blkid $(PARTITION); \
	else \
		echo "$(RED)ERROR: Partition $(PARTITION) not found!$(NC)"; \
		echo "$(YELLOW)Run 'make setup' first to create the partition$(NC)"; \
		exit 1; \
	fi

.PHONY: mount
mount:
	@echo "$(YELLOW)=== Mounting Block Volume ===$(NC)"
	@if [ ! -d $(MOUNT_POINT) ]; then \
		echo "$(CYAN)Creating mount point $(MOUNT_POINT)...$(NC)"; \
		sudo mkdir -p $(MOUNT_POINT); \
	fi
	@if mountpoint -q $(MOUNT_POINT); then \
		echo "$(YELLOW)⚠ $(MOUNT_POINT) is already mounted$(NC)"; \
		mount | grep $(MOUNT_POINT); \
	else \
		echo "$(CYAN)Mounting $(PARTITION) to $(MOUNT_POINT)...$(NC)"; \
		sudo mount $(PARTITION) $(MOUNT_POINT); \
		sudo chown $(VOLUME_OWNER) $(MOUNT_POINT); \
		echo "$(GREEN)✓ Mounted successfully$(NC)"; \
		echo "$(CYAN)Mount details:$(NC)"; \
		mount | grep $(MOUNT_POINT); \
	fi

.PHONY: permanent
permanent:
	@echo "$(YELLOW)=== Making Mount Permanent ===$(NC)"
	@# Refresh UUID after format
	$(

#  /etc/docker/daemon.json
        {
  "data-root": "/data/docker",
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3",
    "compress": "true"
  },
  "default-ulimits": {
    "memlock": {
      "Name": "memlock",
      "Hard": -1,
      "Soft": -1
    }
  },
  "live-restore": true,
  "userland-proxy": false,
  "ip-forward": true,
  "iptables": true
}
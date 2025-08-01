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
COMPOSE_BASE = docker-compose.yml
COMPOSE_DEV = docker-compose.dev.yml
COMPOSE_PROD = docker-compose.prod.yml

# Docker Configuration
DOCKER_COMPOSE_VERSION = 2.23.0
DOCKER_NETWORK = trading-network

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
	@echo "$(CYAN)Primary Commands:$(NC)"
	@echo "  $(GREEN)make deploy$(NC)             - Deploy trading application in production mode"
	@echo "  $(GREEN)make dev-up$(NC)              - Start all services in development mode"
	@echo "  $(GREEN)make prod-up$(NC)             - Start all services in production mode"
	@echo "  $(GREEN)make down$(NC)                - Stop all services"
	@echo ""
	@echo "$(CYAN)Full Setup Commands:$(NC)"
	@echo "  $(GREEN)make complete-setup$(NC)     - Run full setup (volume + trading system)"
	@echo "  $(GREEN)make volume-setup$(NC)       - Setup block volume only"
	@echo ""
	@echo "$(CYAN)Block Volume Commands:$(NC)"
	@echo "  $(GREEN)make check$(NC)              - Check current disk status"
	@echo "  $(GREEN)make setup$(NC)              - Create partition on block device"
	@echo "  $(GREEN)make format$(NC)             - Format the volume ($(RED)DESTROYS DATA!$(NC))"
	@echo "  $(GREEN)make mount$(NC)              - Mount the volume temporarily"
	@echo "  $(GREEN)make permanent$(NC)          - Add to /etc/fstab for permanent mounting"
	@echo "  $(GREEN)make test$(NC)               - Test the volume setup"
	@echo ""
	@echo "$(CYAN)Trading System Sub-Commands:$(NC)"
	@echo "  $(GREEN)make install-docker$(NC)     - Install Docker and Docker Compose"
	@echo "  $(GREEN)make trading-bootstrap$(NC)  - Bootstrap trading system (first time)"
	@echo "  $(GREEN)make trading-unlock$(NC)     - Unlock system after verification"
	@echo "  $(GREEN)make trading-status$(NC)     - Check trading system status"
	@echo "  $(GREEN)make trading-logs$(NC)       - View trading system logs"
	@echo ""
	@echo "$(YELLOW)For detailed help on any command, run: make help-<command>$(NC)"
	@echo "$(BLUE)================================================================$(NC)"

# =======================
# TOP-LEVEL APP COMMANDS
# =======================
.PHONY: deploy dev-up prod-up down trading-status trading-logs

deploy: check-docker
	@echo "$(BLUE)--- Deploying Trading System in Production Mode ---$(NC)"
	@echo "$(YELLOW)Step 1: Applying system optimizations...$(NC)"
	sudo bash scripts/optimize-system.sh
	@echo "$(YELLOW)Step 2: Starting production services...$(NC)"
	$(MAKE) prod-up
	@echo "$(GREEN)✓ Deployment complete. Run 'make trading-status' to check services.$(NC)"

dev-up: check-docker
	@echo "$(BLUE)--- Starting Development Environment ---$(NC)"
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_DEV) up -d --build
	@echo "$(GREEN)✓ Development services are up. Run 'make trading-status' to check.$(NC)"

prod-up: check-docker
	@echo "$(BLUE)--- Starting Production Environment ---$(NC)"
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PROD) up -d --build
	@echo "$(GREEN)✓ Production services are up. Run 'make trading-status' to check.$(NC)"

down:
	@echo "$(BLUE)--- Stopping all environments ---$(NC)"
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_DEV) down
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PROD) down --remove-orphans

trading-status:
	@echo "$(YELLOW)=== Checking Service Status ===$(NC)"
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PROD) ps

trading-logs:
	@echo "$(YELLOW)=== Tailing Production Logs (Ctrl+C to exit) ===$(NC)"
	docker compose -f $(COMPOSE_BASE) -f $(COMPOSE_PROD) logs -f --tail=100

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
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "1. Run the deployment: $(CYAN)make deploy$(NC)"
	@echo "2. Create secret files if you haven't yet."
	@echo "3. Bootstrap the system: $(CYAN)make trading-bootstrap$(NC)"
	@echo "4. Verify and unlock: $(CYAN)make trading-unlock$(NC)"

volume-setup: check setup format mount permanent selinux-fix test create-directories
	@echo "$(GREEN)✓ Block volume setup complete!$(NC)"

trading-setup: check-docker
	@echo "$(YELLOW)Trading system codebase setup (e.g., git clone) should be done here.$(NC)"
	@echo "$(GREEN)✓ Trading system setup hooks complete!$(NC)"

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
```

<!-- /etc/docker/daemon.json -->
```json
{
  "data-root": "/data/docker",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

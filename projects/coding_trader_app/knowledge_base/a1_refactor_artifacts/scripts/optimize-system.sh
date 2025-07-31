#!/bin/bash

# A1.Flex System Optimization Script
# Applies kernel settings for high-performance networking and database workloads.
# Run with sudo: sudo bash scripts/optimize-system.sh

echo "Applying system optimizations for high-throughput trading..."

# Increase system's connection queue capacity
# Helps prevent connection drops under high load
echo "net.core.somaxconn=1024" | sudo tee -a /etc/sysctl.conf

# Allow fast reuse of sockets in TIME_WAIT state
# Important for applications with many short-lived connections
echo "net.ipv4.tcp_tw_reuse=1" | sudo tee -a /etc/sysctl.conf

# Increase the maximum number of open file descriptors
echo "fs.file-max=200000" | sudo tee -a /etc/sysctl.conf

# Configure memory overcommit for Redis/Postgres performance
# 1 = Always overcommit, which is beneficial for Redis's fork-on-write save
echo "vm.overcommit_memory=1" | sudo tee -a /etc/sysctl.conf

# Apply settings immediately
sudo sysctl -p

echo "Optimizations applied and set to be persistent across reboots."

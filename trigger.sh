#!/bin/bash

# Claude HTTP Trigger Script
# This script is called by Claude hooks to trigger HTTP notifications

# Log that hook was called for debugging
echo "$(date): HTTP trigger called" >> /tmp/claude-hook-debug.log

# Make POST request to local HTTP notifier service
curl -s -X POST http://localhost:8765/trigger > /dev/null 2>&1

# Exit successfully
exit 0
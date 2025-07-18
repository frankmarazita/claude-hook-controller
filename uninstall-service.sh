#!/bin/bash

# Claude Hook Controller - Service Uninstallation Script

set -e

SERVICE_NAME="claude-hook-controller.service"
USER_SERVICE_DIR="${HOME}/.config/systemd/user"
TARGET_SERVICE_FILE="${USER_SERVICE_DIR}/${SERVICE_NAME}"

echo "Uninstalling Claude Hook Controller systemd user service..."

# Check if service is installed
if [[ ! -f "$TARGET_SERVICE_FILE" ]]; then
    echo "Service not found at $TARGET_SERVICE_FILE"
    echo "Service may not be installed or already removed."
    exit 0
fi

# Stop the service if running
echo "Stopping service..."
systemctl --user stop "$SERVICE_NAME" 2>/dev/null || echo "Service was not running"

# Disable the service
echo "Disabling service..."
systemctl --user disable "$SERVICE_NAME" 2>/dev/null || echo "Service was not enabled"

# Remove service file
echo "Removing service file..."
rm -f "$TARGET_SERVICE_FILE"

# Reload systemd user daemon
echo "Reloading systemd user daemon..."
systemctl --user daemon-reload

# Reset failed state if any
systemctl --user reset-failed "$SERVICE_NAME" 2>/dev/null || true

echo ""
echo "Uninstallation complete!"
echo "The Claude Hook Controller service has been removed."
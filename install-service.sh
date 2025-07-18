#!/bin/bash

# Claude Hook Controller - Service Installation Script

set -e

SERVICE_NAME="claude-hook-controller.service"
SERVICE_FILE="$(dirname "$0")/${SERVICE_NAME}"
USER_SERVICE_DIR="${HOME}/.config/systemd/user"
TARGET_SERVICE_FILE="${USER_SERVICE_DIR}/${SERVICE_NAME}"

echo "Installing Claude Hook Controller as a systemd user service..."

# Check if service file exists
if [[ ! -f "$SERVICE_FILE" ]]; then
    echo "Error: Service file $SERVICE_FILE not found!"
    exit 1
fi

# Create user systemd directory if it doesn't exist
mkdir -p "$USER_SERVICE_DIR"

# Copy service file
echo "Copying service file to $TARGET_SERVICE_FILE"
cp "$SERVICE_FILE" "$TARGET_SERVICE_FILE"

# Reload systemd user daemon
echo "Reloading systemd user daemon..."
systemctl --user daemon-reload

# Enable the service
echo "Enabling service..."
systemctl --user enable "$SERVICE_NAME"

# Start the service
echo "Starting service..."
systemctl --user start "$SERVICE_NAME"

# Check status
echo "Service status:"
systemctl --user status "$SERVICE_NAME" --no-pager

echo ""
echo "Installation complete!"
echo ""
echo "Service management commands:"
echo "  Start:   systemctl --user start $SERVICE_NAME"
echo "  Stop:    systemctl --user stop $SERVICE_NAME"
echo "  Restart: systemctl --user restart $SERVICE_NAME"
echo "  Status:  systemctl --user status $SERVICE_NAME"
echo "  Logs:    journalctl --user -u $SERVICE_NAME -f"
echo ""
echo "To disable auto-start: systemctl --user disable $SERVICE_NAME"
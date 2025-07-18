# Claude Hook Controller

A system tray application that provides toggleable HTTP notifications for Claude Code hooks. This tool allows you to control when and how Claude Code hooks trigger external HTTP requests, making it perfect for integrating Claude with other services while maintaining full control over when notifications are sent.

## Features

- **System Tray Integration**: Cross-platform system tray icon with visual status indicator
- **Toggle Control**: Easy on/off switching via system tray menu or left-click
- **HTTP Server**: Local HTTP server that receives trigger requests from Claude hooks
- **Persistent Settings**: Configuration automatically saved between sessions
- **Configurable Target**: Set your own target URL for HTTP notifications
- **Hook Integration**: Seamlessly integrates with Claude Code's hook system

## Quick Start

1. **Install dependencies:**

   ```bash
   uv sync
   ```

2. **Run the application:**

   ```bash
   uv run python hook-controller.py
   ```

3. **Set up Claude Code hook:**
   Add the trigger script to your Claude Code hooks configuration (see Hook Configuration section below).

## Files

- `hook-controller.py` - Main system tray application
- `trigger.sh` - Hook script that sends HTTP requests to the controller
- `pyproject.toml` - Project configuration and dependencies
- `claude-hook-controller.service` - Systemd service file for automatic startup
- `install-service.sh` - Service installation script
- `uninstall-service.sh` - Service removal script
- `README.md` - This documentation

## Configuration

Settings are automatically stored in `config.json` when you first run the application:

```json
{
  "enabled": true,
  "port": 8765,
  "target_url": "https://your-webhook-url.com"
}
```

### Configuration Options

- `enabled`: Whether the service processes trigger requests (boolean)
- `port`: Local port for the HTTP server (default: 8765)
- `target_url`: The URL that will receive HTTP GET requests when triggered

## Usage

### System Tray Interface

- **Green circle**: Service enabled - will make HTTP requests when triggered
- **Red circle**: Service disabled - ignores trigger requests
- **Left-click**: Toggle enabled/disabled state
- **Right-click**: Access full menu with status and controls

### Manual Testing

Test the HTTP trigger manually:

```bash
curl -X POST http://localhost:8765/trigger
```

### Integration with Claude Code

The `trigger.sh` script is designed to be used as a Claude Code hook. When Claude completes a task, it will call this script, which sends a POST request to the local HTTP server. If enabled, the controller then makes a GET request to your configured target URL.

## Hook Configuration

To integrate with Claude Code, you need to configure the trigger script as a hook in your Claude settings. Claude Code hooks are defined in `~/.claude/settings.json`.

### What are Claude Code Hooks?

Claude Code hooks are scripts that run automatically when specific events occur during Claude's operation. They allow you to extend Claude's functionality by triggering custom actions like notifications, logging, or integrations with external services. The most common hook type is "Stop", which runs when Claude completes a task.

### Adding the Hook

1. **Edit your Claude settings file:**

   ```bash
   nano ~/.claude/settings.json
   ```

2. **Add the hook configuration:**
   ```json
   {
     "hooks": {
       "Stop": [
         {
           "hooks": [
             {
               "type": "command",
               "command": "/path/to/the/repo/trigger.sh"
             }
           ]
         }
       ]
     }
   }
   ```

Remember to replace `/path/to/the/repo/` with the actual path to your cloned repository where `trigger.sh` is located.

### Verification

After configuring the hook, you can verify it's working by:

1. Running a Claude Code task
2. Checking the debug log: `tail -f /tmp/claude-hook-debug.log`
3. Observing the system tray icon for HTTP requests being made

## How It Works

1. **Claude Code Hook**: Claude executes `trigger.sh` when completing tasks
2. **Local HTTP Request**: Script sends POST to `localhost:8765/trigger`
3. **Controller Processing**: If enabled, controller makes GET request to configured URL
4. **External Integration**: Your external service receives the notification

## Dependencies

- Python 3.7+
- PyQt5 (for system tray functionality)
- requests (for HTTP requests)
- uv (for dependency management)

## Installation Options

### Development

```bash
git clone https://github.com/frankmarazita/claude-hook-controller.git
cd claude-hook-controller
uv sync
uv run python hook-controller.py
```

### Production (Systemd Service)

For production use, install as a systemd user service for automatic startup:

```bash
git clone https://github.com/frankmarazita/claude-hook-controller.git
cd claude-hook-controller
uv sync
./install-service.sh
```

The service will:

- Start automatically when you log in
- Restart automatically if it crashes
- Run in the background as a system tray application

### Service Management

```bash
# Check service status
systemctl --user status claude-hook-controller.service

# Start/stop/restart service
systemctl --user start claude-hook-controller.service
systemctl --user stop claude-hook-controller.service
systemctl --user restart claude-hook-controller.service

# View service logs
journalctl --user -u claude-hook-controller.service -f

# Disable auto-start
systemctl --user disable claude-hook-controller.service

# Remove service completely
./uninstall-service.sh
```

## Use Cases

- **Webhook Integration**: Trigger webhooks when Claude completes tasks
- **Team Notifications**: Send notifications to Slack, Discord, or other chat platforms
- **CI/CD Integration**: Trigger builds or deployments after Claude code changes
- **Monitoring**: Log Claude activity to external monitoring systems
- **Custom Workflows**: Integrate with any HTTP-based service or API

## Troubleshooting

### System Tray Not Visible

Ensure your desktop environment supports system tray applications. On some Linux distributions, you may need to install additional packages or enable system tray support.

### Port Already in Use

If port 8765 is already in use, modify the `port` setting in your configuration file.

### HTTP Requests Not Working

Check that:

1. The controller is running and enabled (green icon)
2. Your target URL is accessible
3. No firewall is blocking the requests

### Service Issues

If the systemd service is not working:

1. **Check service status:**

   ```bash
   systemctl --user status claude-hook-controller.service
   ```

2. **View service logs:**

   ```bash
   journalctl --user -u claude-hook-controller.service -f
   ```

3. **Ensure graphical session is available:**
   The service requires a graphical session (system tray). If running headless, the service won't work.

4. **Check dependencies:**
   ```bash
   cd ~/repos/claude-hook-controller
   uv sync
   ```

### Hook Configuration Issues

If the hook is not triggering:

1. **Verify hook script path in settings.json:**
   Ensure the path in your settings.json matches the actual location of trigger.sh

2. **Test hook script manually:**

```bash
./trigger.sh
```

3. **Restart Claude Code:**
   After changing hook configuration, restart Claude Code to reload settings

## License

This project is available under the MIT License.

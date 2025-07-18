#!/usr/bin/env -S uv run python
"""
Claude Hook Controller - System Tray App
Provides a toggleable HTTP notification service for Claude Code hooks.
"""

import sys
import json
import requests
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor

CONFIG_FILE = Path.cwd() / 'config.json'
DEFAULT_CONFIG = {
    'enabled': True,
    'port': 8765,
    'target_url': 'https://example.com'
}

class Config:
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return {**DEFAULT_CONFIG, **json.load(f)}
            except Exception:
                # If file exists but can't be read, create a new one with defaults
                config = DEFAULT_CONFIG.copy()
                self._create_config_file(config)
                return config
        else:
            # Create config file with defaults on first run
            config = DEFAULT_CONFIG.copy()
            self._create_config_file(config)
            return config
    
    def _create_config_file(self, config):
        """Create the config file with the given configuration"""
        CONFIG_FILE.parent.mkdir(exist_ok=True)
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    
    def save_config(self):
        self._create_config_file(self.config)
    
    def get(self, key):
        return self.config.get(key)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()
    
    def reload(self):
        """Reload config from file"""
        self.config = self.load_config()

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, config, *args, **kwargs):
        self.config = config
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        if self.path == '/trigger':
            # Reload config to get latest values
            self.config.reload()
            
            if self.config.get('enabled'):
                try:
                    target_url = self.config.get('target_url')
                    response = requests.get(target_url, timeout=10)
                    self.send_response(200)
                    self.end_headers()
                    self.wfile.write(f"GET request sent to {target_url}, status: {response.status_code}".encode())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(f"Error: {str(e)}".encode())
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Service disabled")
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        # Suppress HTTP server logs
        pass

class HTTPServerThread(QThread):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.server = None
    
    def run(self):
        handler = lambda *args, **kwargs: HTTPRequestHandler(self.config, *args, **kwargs)
        self.server = HTTPServer(('localhost', self.config.get('port')), handler)
        self.server.serve_forever()
    
    def stop(self):
        if self.server:
            self.server.shutdown()

class SystemTrayApp:
    def __init__(self):
        self.config = Config()
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # Create system tray icon
        self.tray_icon = QSystemTrayIcon()
        self.update_icon()
        
        # Connect click handler for toggle
        self.tray_icon.activated.connect(self.icon_clicked)
        
        # Create menu
        self.create_menu()
        
        # Start HTTP server
        self.server_thread = HTTPServerThread(self.config)
        self.server_thread.start()
        
        self.tray_icon.show()
    
    def create_icon(self, enabled=True):
        """Create a colored icon based on enabled state"""
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle
        color = QColor(0, 255, 0) if enabled else QColor(255, 0, 0)
        painter.setBrush(QBrush(color))
        painter.drawEllipse(4, 4, 24, 24)
        
        # Draw 'C' for Claude
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(10, 20, "C")
        
        painter.end()
        return QIcon(pixmap)
    
    def update_icon(self):
        enabled = self.config.get('enabled')
        self.tray_icon.setIcon(self.create_icon(enabled))
        status = "enabled" if enabled else "disabled"
        self.tray_icon.setToolTip(f"Claude Hook Controller ({status})")
    
    def create_menu(self):
        menu = QMenu()
        
        # Toggle action
        self.toggle_action = QAction("Disable" if self.config.get('enabled') else "Enable")
        self.toggle_action.triggered.connect(self.toggle_service)
        menu.addAction(self.toggle_action)
        
        menu.addSeparator()
        
        # Status action
        status = "Enabled" if self.config.get('enabled') else "Disabled"
        status_action = QAction(f"Status: {status}")
        status_action.setEnabled(False)
        menu.addAction(status_action)
        
        # Port info
        port_action = QAction(f"Port: {self.config.get('port')}")
        port_action.setEnabled(False)
        menu.addAction(port_action)
        
        menu.addSeparator()
        
        # Quit action
        quit_action = QAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def icon_clicked(self, reason):
        """Handle system tray icon clicks"""
        if reason == QSystemTrayIcon.Trigger:  # Left click
            self.toggle_service()
    
    def toggle_service(self):
        current_state = self.config.get('enabled')
        new_state = not current_state
        self.config.set('enabled', new_state)
        
        self.update_icon()
        self.create_menu()  # Refresh menu
        
        # Show notification
        status = "enabled" if new_state else "disabled"
        self.tray_icon.showMessage(
            "Claude Hook Controller",
            f"Service {status}",
            QSystemTrayIcon.Information,
            2000
        )
    
    def quit_app(self):
        self.server_thread.stop()
        self.server_thread.wait()
        self.app.quit()
    
    def run(self):
        return self.app.exec_()

if __name__ == '__main__':
    app = SystemTrayApp()
    sys.exit(app.run())

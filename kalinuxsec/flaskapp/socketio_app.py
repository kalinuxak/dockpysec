from flask_socketio import emit, disconnect
import psutil
import threading
import time
from . import socketio
from flask import current_app
import requests

def emit_system_metrics(app):
    with app.app_context():
        while True:
            metrics = {
                "cpu": psutil.cpu_percent(interval=1),
                "memory": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
                "network": {
                    "sent": psutil.net_io_counters().bytes_sent,
                    "recv": psutil.net_io_counters().bytes_recv,
                },
            }
            socketio.emit("system_metrics", metrics)  # Broadcast to all connected clients
            time.sleep(1)

def start_background_task(app):
    """Start a background thread for emitting system metrics."""
    thread = threading.Thread(target=emit_system_metrics, args=(app,), daemon=True)
    thread.start()

@socketio.on("connect")
def handle_connect():
    print("Client connected")
    emit("my response", {"data": "Connected to the server!"})

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

"""
AVA Network Detection

Simple connectivity checker for online/offline status.
"""

import socket
import logging
import threading
from typing import Callable, Optional

logger = logging.getLogger(__name__)


def check_connectivity(host: str = "8.8.8.8", port: int = 53, timeout: float = 2.0) -> bool:
    """
    Check internet connectivity by attempting a DNS lookup.
    
    Args:
        host: Host to check (default: Google DNS)
        port: Port to check
        timeout: Connection timeout in seconds
        
    Returns:
        True if connected, False otherwise
    """
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((host, port))
            return True
        except (socket.error, OSError):
            return False
        finally:
            sock.close()
    except (socket.error, OSError):
        return False


class NetworkMonitor:
    """Monitors network connectivity in the background."""
    
    def __init__(self, check_interval: int = 30):
        """
        Initialize network monitor.
        
        Args:
            check_interval: Seconds between connectivity checks
        """
        self._check_interval = check_interval
        self._is_online = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._running = False
        self._on_status_change: Optional[Callable[[bool], None]] = None
    
    def set_callback(self, callback: Callable[[bool], None]) -> None:
        """Set callback for connectivity changes."""
        self._on_status_change = callback
    
    def start(self) -> None:
        """Start monitoring connectivity."""
        if self._running:
            return
        
        self._running = True
        # Do initial check
        self._check()
        # Start background monitor
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()
        logger.info("Network monitor started")
    
    def stop(self) -> None:
        """Stop monitoring."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=5)
        logger.info("Network monitor stopped")
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while self._running:
            import time
            time.sleep(self._check_interval)
            if self._running:
                self._check()
    
    def _check(self) -> None:
        """Perform connectivity check."""
        was_online = self._is_online
        self._is_online = check_connectivity()
        
        if was_online != self._is_online and self._on_status_change:
            self._on_status_change(self._is_online)
    
    @property
    def is_online(self) -> bool:
        """Current connectivity status."""
        return self._is_online

import logging
from typing import Dict, Optional
from .device_handler import F5DeviceHandler

logger = logging.getLogger(__name__)

class DeviceManager:
    """Manages device handlers for reuse across API endpoints."""
    
    # Singleton instance
    _instance = None
    
    # Handler cache
    _handlers: Dict[str, F5DeviceHandler] = {}
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super(DeviceManager, cls).__new__(cls)
        return cls._instance
    
    def get_handler(self, device_ip: str, username: str, password: str) -> F5DeviceHandler:
        """Get or create a device handler for the specified device.
        
        Args:
            device_ip: IP address of the device
            username: Authentication username
            password: Authentication password
            
        Returns:
            F5DeviceHandler instance for the device
        """
        cache_key = f"{device_ip}:{username}"
        
        if cache_key not in self._handlers:
            logger.info(f"Creating new device handler for {device_ip}")
            self._handlers[cache_key] = F5DeviceHandler(device_ip, username, password)
        else:
            logger.info(f"Reusing existing device handler for {device_ip}")
        
        return self._handlers[cache_key]
    
    def close_handler(self, device_ip: str, username: str):
        """Close a specific device handler.
        
        Args:
            device_ip: IP address of the device
            username: Authentication username
        """
        cache_key = f"{device_ip}:{username}"
        
        if cache_key in self._handlers:
            logger.info(f"Closing device handler for {device_ip}")
            self._handlers[cache_key].close()
            del self._handlers[cache_key]
    
    def close_all(self):
        """Close all device handlers."""
        logger.info(f"Closing all device handlers ({len(self._handlers)} handlers)")
        for handler in self._handlers.values():
            handler.close()
        self._handlers.clear() 
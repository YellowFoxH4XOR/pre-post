from netmiko import ConnectHandler
from typing import List, Dict, Any, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
from contextlib import contextmanager
from pathlib import Path
from ..utils.command_validator import validate_read_only_commands

# Configure logging
logger = logging.getLogger(__name__)


class F5DeviceHandler:
    """Handler for F5 device connections with connection reuse."""
    
    # Class-level connection cache to persist connections between instances
    _connection_cache = {}
    
    def __init__(self, device_ip: str, username: str, password: str):
        """Initialize device handler with connection parameters.
        
        Args:
            device_ip: IP address of the device
            username: Authentication username
            password: Authentication password
        """
        self.device_ip = device_ip
        self.device_info = {
            'device_type': 'f5_ltm',
            'ip': device_ip,
            'username': username,
            'password': password,
        }
        
        # Ensure logs directory exists
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Add session logging
        self.device_info['session_log'] = f"logs/netmiko_{device_ip}.log"
        
        # Cache key for this connection
        self.cache_key = f"{device_ip}:{username}"
    
    @contextmanager
    def get_connection(self):
        """Context manager for getting and releasing a Netmiko connection.
        
        Uses a class-level connection cache to reuse connections across
        multiple instances of F5DeviceHandler for the same device.
        
        Yields:
            netmiko.ConnectHandler: Active connection to the device
        """
        try:
            # Check if connection exists in cache
            if (self.cache_key in self._connection_cache and 
                    self._connection_cache[self.cache_key] is not None):
                logger.info(f"Reusing existing connection to device: {self.device_ip}")
                connection = self._connection_cache[self.cache_key]
                # Verify connection is still active
                if not connection.is_alive():
                    logger.warning(
                        f"Cached connection to {self.device_ip} is not alive, reconnecting..."
                    )
                    connection.disconnect()
                    self._connection_cache[self.cache_key] = None
                    connection = None
            else:
                connection = None
            
            # Establish new connection if needed
            if connection is None:
                logger.info(f"Opening new connection to device: {self.device_ip}")
                connection = ConnectHandler(**self.device_info)
                self._connection_cache[self.cache_key] = connection
            
            yield connection
        except Exception as e:
            # Close and remove the connection on error
            logger.exception(f"Error with connection to {self.device_ip}: {str(e)}")
            if (self.cache_key in self._connection_cache and 
                    self._connection_cache[self.cache_key] is not None):
                try:
                    self._connection_cache[self.cache_key].disconnect()
                except Exception:
                    pass  # Ignore errors while disconnecting
                self._connection_cache[self.cache_key] = None
            raise
    
    def _validate_show_commands(self, commands: List[str]) -> List[str]:
        """Validate that all commands are read-only commands for safety."""
        is_valid, validated_commands, invalid_commands = validate_read_only_commands(commands)
        
        if not is_valid:
            error_msg = f"Only show, tmsh, cat, list, and display commands are allowed. Invalid commands: {', '.join(invalid_commands)}"
            logger.error(f"Command validation failed for {self.device_ip}: {error_msg}")
            raise ValueError(error_msg)
        
        return validated_commands
    
    def _execute_commands(self, commands: List[str]) -> Dict[str, Any]:
        """Execute multiple commands on the device using a single session.
        
        Args:
            commands: List of commands to execute
            
        Returns:
            Dict containing status and results or error information
        """
        results = {}
        try:
            # Validate commands before execution
            validated_commands = self._validate_show_commands(commands)
            
            with self.get_connection() as net_connect:
                logger.info(
                    f"Using connection to execute {len(validated_commands)} commands on device: "
                    f"{self.device_ip}"
                )
                
                for command in validated_commands:
                    logger.info(f"Executing command on {self.device_ip}: {command}")
                    output = net_connect.send_command(command)
                    results[command] = output
                    logger.debug(f"Command output length: {len(output)} characters")
            
            logger.info(f"Successfully executed all commands on device: {self.device_ip}")
            return {"status": "success", "results": results}
        except ValueError as ve:
            # Specific handling for validation errors
            logger.error(f"Command validation error: {str(ve)}")
            return {"status": "error", "error": str(ve)}
        except Exception as e:
            logger.exception(f"Error executing commands on device {self.device_ip}: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def execute_commands_async(self, commands: List[str]) -> Dict[str, Any]:
        """Execute commands asynchronously using a ThreadPoolExecutor.
        
        Args:
            commands: List of commands to execute
            
        Returns:
            Dict containing status and results or error information
        """
        logger.info(
            f"Executing commands asynchronously on device: {self.device_ip}, "
            f"commands: {commands}"
        )
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool, self._execute_commands, commands
            )
        
        if result["status"] == "success":
            logger.info(f"Commands executed successfully on device: {self.device_ip}")
        else:
            logger.error(
                f"Failed to execute commands on device: {self.device_ip}, "
                f"error: {result.get('error', 'Unknown error')}"
            )
        
        return result
    
    def close(self):
        """Explicitly close the connection when done."""
        if (self.cache_key in self._connection_cache and 
                self._connection_cache[self.cache_key] is not None):
            logger.info(f"Closing connection to device: {self.device_ip}")
            try:
                self._connection_cache[self.cache_key].disconnect()
            except Exception as e:
                logger.warning(f"Error disconnecting from {self.device_ip}: {str(e)}")
            self._connection_cache[self.cache_key] = None
    
    @classmethod
    def close_all_connections(cls):
        """Close all cached connections."""
        for key, connection in cls._connection_cache.items():
            if connection is not None:
                try:
                    logger.info(f"Closing cached connection: {key}")
                    connection.disconnect()
                except Exception as e:
                    logger.warning(f"Error disconnecting for {key}: {str(e)}")
        cls._connection_cache.clear() 
from netmiko import ConnectHandler
from typing import List, Dict, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

class F5DeviceHandler:
    def __init__(self, device_ip: str, username: str, password: str):
        self.device_ip = device_ip
        self.device_info = {
            'device_type': 'f5_ltm',
            'ip': device_ip,
            'username': username,
            'password': password,
        }
    
    def _execute_commands(self, commands: List[str]) -> Dict[str, str]:
        results = {}
        try:
            print(f"Connecting to device: {self.device_info}")
            with ConnectHandler(**self.device_info) as net_connect:
                for command in commands:
                    output = net_connect.send_command(command)
                    results[command] = output
            return {"status": "success", "results": results}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def execute_commands_async(self, commands: List[str]) -> Dict[str, Any]:
        print(f"Executing commands: {commands}")
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(
                pool, self._execute_commands, commands
            )
        print(f"Result: {result}")
        return result 
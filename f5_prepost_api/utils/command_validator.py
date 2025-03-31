import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

def validate_read_only_commands(commands: List[str]) -> Tuple[bool, List[str], List[str]]:
    """Validate that commands are read-only for F5 devices.
    
    Args:
        commands: List of commands to validate
        
    Returns:
        Tuple containing:
            - Boolean indicating if all commands are valid
            - List of validated commands
            - List of invalid commands
    """
    invalid_commands = []
    validated_commands = []
    
    allowed_prefixes = [
        'show ',
        'list ',
        'display ',
        'tmsh ',
        'cat '
    ]
    
    allowed_exact = [
        'show',
        'list',
        'tmsh',
        'cat'
    ]
    
    for command in commands:
        command = command.strip()
        
        # Check exact matches
        if command.lower() in allowed_exact:
            validated_commands.append(command)
            continue
            
        # Check prefix matches
        if any(command.lower().startswith(prefix) for prefix in allowed_prefixes):
            validated_commands.append(command)
            continue
            
        # If we get here, command is invalid
        invalid_commands.append(command)
    
    is_valid = len(invalid_commands) == 0
    
    if not is_valid:
        logger.warning(f"Invalid commands detected: {', '.join(invalid_commands)}")
        
    return is_valid, validated_commands, invalid_commands 
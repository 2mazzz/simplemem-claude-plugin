#!/usr/bin/env python3
"""
SimpleMem Tool: Install
Sets up SimpleMem system for first-time use.
"""

import sys
import json
import subprocess
import os
from pathlib import Path

def install_simplemem():
    """
    Install SimpleMem to /tmp/SimpleMem
    
    Returns:
        dict with success status and message
    """
    try:
        simplemem_dir = Path("/tmp/SimpleMem")
        
        # Check if already installed
        if simplemem_dir.exists() and (simplemem_dir / "main.py").exists():
            return {
                "success": True,
                "message": "SimpleMem already installed",
                "path": str(simplemem_dir),
                "already_installed": True
            }
        
        # Clone repository
        print("Cloning SimpleMem repository...", file=sys.stderr)
        result = subprocess.run(
            ["git", "clone", "https://github.com/aiming-lab/SimpleMem.git", str(simplemem_dir)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Git clone failed: {result.stderr}"
            }
        
        # Install dependencies
        print("Installing dependencies...", file=sys.stderr)
        result = subprocess.run(
            ["pip", "install", "-r", str(simplemem_dir / "requirements.txt"), "--break-system-packages"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Pip install failed: {result.stderr}"
            }
        
        # Create default config if needed
        config_example = simplemem_dir / "config.py.example"
        config_file = simplemem_dir / "config.py"
        
        if config_example.exists() and not config_file.exists():
            print("Creating default config...", file=sys.stderr)
            
            # Read example config
            with open(config_example, 'r') as f:
                config_content = f.read()
            
            # Check for API key in environment
            api_key = os.environ.get("OPENAI_API_KEY", "your-api-key-here")
            
            # Replace placeholder with env var if available
            if api_key != "your-api-key-here":
                config_content = config_content.replace(
                    'OPENAI_API_KEY = None',
                    f'OPENAI_API_KEY = "{api_key}"'
                )
            
            # Write config
            with open(config_file, 'w') as f:
                f.write(config_content)
        
        # Create database directory
        db_dir = Path("/tmp/simplemem_db")
        db_dir.mkdir(exist_ok=True)
        
        return {
            "success": True,
            "message": "SimpleMem installed successfully",
            "path": str(simplemem_dir),
            "db_path": str(db_dir),
            "config_created": config_file.exists(),
            "note": "Remember to set OPENAI_API_KEY in config.py" if api_key == "your-api-key-here" else "Using OPENAI_API_KEY from environment"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Installation timed out"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    result = install_simplemem()
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()

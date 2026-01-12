#!/usr/bin/env python3
"""
SimpleMem Tool: Status
Check SimpleMem installation status and memory statistics.
"""

import sys
import json
import os
import hashlib
from pathlib import Path

# Add SimpleMem to path
SIMPLEMEM_PATH = Path("/tmp/SimpleMem")
sys.path.insert(0, str(SIMPLEMEM_PATH))

def get_project_db_path():
    """Get project-specific database path based on current working directory."""
    cwd = os.getcwd()
    project_hash = hashlib.md5(cwd.encode()).hexdigest()[:16]
    return str(Path.home() / ".claude" / "projects" / f"simplemem-{project_hash}")

def check_status(db_path="/tmp/simplemem_db"):
    """
    Check SimpleMem installation and database status
    
    Returns:
        dict with status information
    """
    status = {
        "installed": False,
        "configured": False,
        "database_exists": False,
        "database_path": db_path,
        "simplemem_path": str(SIMPLEMEM_PATH),
        "errors": []
    }
    
    # Check if SimpleMem is installed
    if SIMPLEMEM_PATH.exists() and (SIMPLEMEM_PATH / "main.py").exists():
        status["installed"] = True
    else:
        status["errors"].append("SimpleMem not installed at /tmp/SimpleMem")
        status["ready"] = False
        return status

    # Check if config exists
    config_file = SIMPLEMEM_PATH / "config.py"
    if config_file.exists():
        status["configured"] = True
        
        # Try to check if API key is set
        try:
            with open(config_file, 'r') as f:
                config_content = f.read()
                if "your-api-key-here" in config_content or "OPENAI_API_KEY = None" in config_content:
                    status["errors"].append("API key not configured in config.py")
                    status["api_key_configured"] = False
                else:
                    status["api_key_configured"] = True
        except Exception as e:
            status["errors"].append(f"Could not read config: {e}")
    else:
        status["configured"] = False
        status["errors"].append("config.py not found - run installation")
    
    # Check database
    db_path_obj = Path(db_path)
    if db_path_obj.exists():
        status["database_exists"] = True

        # Get database size
        try:
            db_size = sum(
                os.path.getsize(os.path.join(dirpath, filename))
                for dirpath, _, filenames in os.walk(db_path_obj)
                for filename in filenames
            )
            status["database_size_mb"] = round(db_size / (1024 * 1024), 2)
        except Exception as e:
            status["errors"].append(f"Could not calculate database size: {e}")
    else:
        status["errors"].append("Database directory not found - will be created on first use")
    
    # Try to import SimpleMem
    try:
        from main import SimpleMemSystem
        status["import_successful"] = True
    except ImportError as e:
        status["import_successful"] = False
        status["errors"].append(f"Cannot import SimpleMem: {e}")
    
    # Overall status
    status["ready"] = (
        status["installed"] and 
        status["configured"] and 
        status.get("import_successful", False)
    )
    
    return status

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Check SimpleMem installation status")
    parser.add_argument("--db-path", default="/tmp/simplemem_db", help="Database path (default: /tmp/simplemem_db)")
    parser.add_argument("--project", action="store_true", help="Use project-specific database")

    args = parser.parse_args()

    # Resolve database path
    if args.project:
        db_path = get_project_db_path()
    else:
        db_path = args.db_path

    status = check_status(db_path=db_path)
    
    # Pretty print
    print(json.dumps(status, indent=2))
    
    # Summary message
    if status["ready"]:
        print("\n✅ SimpleMem is ready to use", file=sys.stderr)
    else:
        print("\n⚠️ SimpleMem has issues:", file=sys.stderr)
        for error in status["errors"]:
            print(f"  - {error}", file=sys.stderr)
        
        if not status["installed"]:
            print("\nRun: python simplemem_install.py", file=sys.stderr)
    
    sys.exit(0 if status["ready"] else 1)

if __name__ == "__main__":
    main()

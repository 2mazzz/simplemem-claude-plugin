#!/usr/bin/env python3
"""
SimpleMem Tool: Recall Memory
Retrieves relevant information from SimpleMem persistent memory system.
"""

import sys
import json
import argparse
import hashlib
import os
from pathlib import Path

# Add SimpleMem to path
SIMPLEMEM_PATH = Path("/tmp/SimpleMem")
sys.path.insert(0, str(SIMPLEMEM_PATH))

try:
    from main import SimpleMemSystem
except ImportError as e:
    print(json.dumps({
        "success": False,
        "error": f"SimpleMem not installed. Run installation first: {e}",
        "context": ""
    }))
    sys.exit(1)

def get_project_db_path():
    """Get project-specific database path based on current working directory."""
    cwd = os.getcwd()
    project_hash = hashlib.md5(cwd.encode()).hexdigest()[:16]
    return str(Path.home() / ".claude" / "projects" / f"simplemem-{project_hash}")

def recall_memory(query, top_k=5, db_path="/tmp/simplemem_db"):
    """
    Query SimpleMem for relevant memories
    
    Args:
        query: Search query string
        top_k: Number of results to return (default: 5)
    
    Returns:
        dict with success status and retrieved context
    """
    try:
        # Initialize memory system
        memory = SimpleMemSystem(
            clear_db=False,
            db_path=db_path
        )
        
        # Query for relevant context
        context = memory.ask(query, top_k=top_k)
        
        if context and context.strip():
            return {
                "success": True,
                "query": query,
                "context": context,
                "found": True,
                "message": f"Found relevant context for: {query}"
            }
        else:
            return {
                "success": True,
                "query": query,
                "context": "",
                "found": False,
                "message": f"No relevant memories found for: {query}"
            }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query,
            "context": "",
            "found": False
        }

def main():
    parser = argparse.ArgumentParser(description="Recall information from SimpleMem")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results (default: 5)")
    parser.add_argument("--json", action="store_true", help="Output as JSON (default)")
    parser.add_argument("--text", action="store_true", help="Output only the context text")
    parser.add_argument("--db-path", default="/tmp/simplemem_db", help="Database path (default: /tmp/simplemem_db)")
    parser.add_argument("--project", action="store_true", help="Use project-specific database")

    args = parser.parse_args()

    # Resolve database path
    if args.project:
        db_path = get_project_db_path()
    else:
        db_path = args.db_path

    # Retrieve memories
    result = recall_memory(query=args.query, top_k=args.top_k, db_path=db_path)
    
    # Output format
    if args.text:
        # Just print the context text (for piping)
        print(result.get("context", ""))
    else:
        # JSON output (default)
        print(json.dumps(result, indent=2))
    
    # Exit code based on success
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()

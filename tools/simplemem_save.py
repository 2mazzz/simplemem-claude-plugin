#!/usr/bin/env python3
"""
SimpleMem Tool: Save Memory
Saves information to the SimpleMem persistent memory system.
"""

import sys
import json
import argparse
import hashlib
import os
from datetime import datetime
from pathlib import Path

# Add SimpleMem to path
SIMPLEMEM_PATH = Path("/tmp/SimpleMem")
sys.path.insert(0, str(SIMPLEMEM_PATH))

try:
    from main import SimpleMemSystem
except ImportError as e:
    print(json.dumps({
        "success": False,
        "error": f"SimpleMem not installed. Run installation first: {e}"
    }))
    sys.exit(1)

def get_project_db_path():
    """Get project-specific database path based on current working directory."""
    cwd = os.getcwd()
    project_hash = hashlib.md5(cwd.encode()).hexdigest()[:16]
    return str(Path.home() / ".claude" / "projects" / f"simplemem-{project_hash}")

def save_memory(content, speaker="User", context="general", metadata=None, db_path="/tmp/simplemem_db"):
    """
    Save content to SimpleMem
    
    Args:
        content: The text to save
        speaker: Who said it (User, Assistant, Note, etc.)
        context: Category/context tag
        metadata: Additional metadata dict
    
    Returns:
        dict with success status and message
    """
    try:
        # Initialize memory system (loads existing)
        memory = SimpleMemSystem(
            clear_db=False,
            db_path=db_path
        )
        
        # Prepare metadata
        full_metadata = {"context": context}
        if metadata:
            full_metadata.update(metadata)
        
        # Add to memory
        memory.add_dialogue(
            speaker=speaker,
            content=content,
            timestamp=datetime.now().isoformat(),
            metadata=full_metadata
        )
        
        # Process and compress
        memory.finalize()
        
        return {
            "success": True,
            "message": f"Saved to memory: {content[:60]}{'...' if len(content) > 60 else ''}",
            "speaker": speaker,
            "context": context,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def save_conversation(user_message, assistant_message, context="general", db_path="/tmp/simplemem_db"):
    """
    Save a full conversation turn (user + assistant)

    Args:
        user_message: User's message
        assistant_message: Assistant's response
        context: Conversation category
        db_path: Database path (default: /tmp/simplemem_db)

    Returns:
        dict with success status
    """
    try:
        memory = SimpleMemSystem(clear_db=False, db_path=db_path)
        
        timestamp = datetime.now().isoformat()
        
        # Save user message
        memory.add_dialogue(
            speaker="User",
            content=user_message,
            timestamp=timestamp,
            metadata={"context": context}
        )
        
        # Save assistant message
        memory.add_dialogue(
            speaker="Assistant",
            content=assistant_message,
            timestamp=timestamp,
            metadata={"context": context}
        )
        
        memory.finalize()
        
        return {
            "success": True,
            "message": f"Saved conversation to memory (context: {context})",
            "context": context,
            "timestamp": timestamp
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    parser = argparse.ArgumentParser(description="Save information to SimpleMem")
    parser.add_argument("content", help="Content to save")
    parser.add_argument("--speaker", default="User", help="Speaker name (default: User)")
    parser.add_argument("--context", default="general", help="Context/category tag")
    parser.add_argument("--assistant-message", help="If provided, saves as conversation with user message")
    parser.add_argument("--metadata", help="Additional metadata as JSON string")
    parser.add_argument("--db-path", default="/tmp/simplemem_db", help="Database path (default: /tmp/simplemem_db)")
    parser.add_argument("--project", action="store_true", help="Use project-specific database")

    args = parser.parse_args()

    # Resolve database path
    if args.project:
        db_path = get_project_db_path()
    else:
        db_path = args.db_path
    
    # Parse metadata if provided
    metadata = None
    if args.metadata:
        try:
            metadata = json.loads(args.metadata)
        except json.JSONDecodeError:
            print(json.dumps({
                "success": False,
                "error": "Invalid metadata JSON"
            }))
            sys.exit(1)
    
    # Save conversation or single message
    if args.assistant_message:
        result = save_conversation(
            user_message=args.content,
            assistant_message=args.assistant_message,
            context=args.context,
            db_path=db_path
        )
    else:
        result = save_memory(
            content=args.content,
            speaker=args.speaker,
            context=args.context,
            metadata=metadata,
            db_path=db_path
        )
    
    # Output result as JSON
    print(json.dumps(result, indent=2))
    
    # Exit code based on success
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()

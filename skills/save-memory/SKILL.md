# Save to Memory Skill

Save important information to SimpleMem persistent memory system.

## When to Use

Automatically invoke this skill when the user:
- Asks to remember or save something ("Remember this", "Save this", "Don't forget", "Keep in mind", etc.)
- Shares important information they want preserved (decisions, preferences, discoveries, code snippets, etc.)
- After generating a `/compact` summary - save the summary to memory automatically
- When working on long-term projects and important context is shared

## How to Invoke

```bash
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "<CONTENT>" --project [OPTIONS]
```

### Basic Usage (Project-Specific - Recommended)

```bash
# Save a simple fact
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "I prefer morning meetings" --project

# Save with context tag
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "Database password in .env" --context security --project

# Save with custom speaker
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "Deadline is Dec 15" --speaker "Note" --context project --project
```

### Save Conversation (User + Assistant)

```bash
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "User question here" \
  --assistant-message "Your response here" \
  --context topic --project
```

### Global Memory (Optional)

```bash
# Omit --project flag to save to global memory (shared across all projects)
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "Information to share globally"
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `content` | Information to save (required) | - |
| `--project` | Use project-specific memory (recommended) | Global memory |
| `--context` | Category/tag for the information | "general" |
| `--speaker` | Who said it (User, Assistant, Note, etc.) | "User" |
| `--assistant-message` | For saving Q&A pairs - the assistant's response | - |
| `--metadata` | Additional JSON metadata | - |
| `--db-path` | Custom database path (advanced) | - |

## Output Format

Success:
```json
{
  "success": true,
  "message": "Saved to memory: I prefer morning meetings...",
  "speaker": "User",
  "context": "general",
  "timestamp": "2025-01-12T14:30:00"
}
```

Error:
```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

## Examples

### Save a preference
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "I prefer PostgreSQL over MySQL for production databases" --context database --project
```

### Save a decision
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "Decided to use Docker for deployment" --context deployment --project
```

### Save code discovery
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "Found that using useCallback prevents unnecessary re-renders in React" --context react --project
```

### Save a conversation exchange
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "How do I optimize database queries?" \
  --assistant-message "Use indexes on frequently queried columns, consider query caching with Redis, and analyze query plans with EXPLAIN" \
  --context database --project
```

## Prerequisites

Before using this skill:
1. Check SimpleMem is installed: `python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project`
2. If not installed, run: `python ~/.claude/plugins/simplemem/tools/simplemem_install.py`
3. Set OPENAI_API_KEY environment variable or edit `/tmp/SimpleMem/config.py`

## Notes

- **Project-Specific Memory**: Information is isolated per project (recommended)
- **Automatic Compression**: SimpleMem automatically compresses and indexes information using semantic search
- **Timestamps**: All saved information is automatically timestamped
- **JSON Output**: Parse the JSON response to confirm success or handle errors

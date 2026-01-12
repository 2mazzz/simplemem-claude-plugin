# Recall from Memory Skill

Retrieve relevant information from SimpleMem persistent memory system using semantic search.

## When to Use

Automatically invoke this skill when the user:
- Asks to remember or recall something ("What did I tell you about...", "Remind me", "Do you remember...", etc.)
- Asks a question that might have been discussed in previous sessions
- Working on a long-term project and relevant past context would help answer the question
- You detect the question relates to previous conversations in the project

## How to Invoke

```bash
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "<QUERY>" --project [OPTIONS]
```

### Basic Usage (Project-Specific - Recommended)

```bash
# Search for relevant memories
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "meeting preferences" --project

# Get more results (default is 5)
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "database decisions" --top-k 10 --project

# Get just the text output (useful for piping/parsing)
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "meeting preferences" --text --project
```

### Global Memory (Optional)

```bash
# Search global memory (shared across all projects)
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "general preference"
```

## Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query (required) | - |
| `--project` | Search project-specific memory (recommended) | Search global |
| `--top-k` | Number of results to return | 5 |
| `--text` | Output as plain text instead of JSON | JSON output |
| `--json` | Explicitly request JSON output | - |
| `--db-path` | Custom database path (advanced) | - |

## Output Format

### JSON Output (default)

Success with results:
```json
{
  "success": true,
  "query": "meeting preferences",
  "found": true,
  "context": "I prefer morning meetings, not after 3pm...",
  "message": "Found relevant context for: meeting preferences"
}
```

Success without results:
```json
{
  "success": true,
  "query": "meeting preferences",
  "found": false,
  "context": "",
  "message": "No relevant memories found for: meeting preferences"
}
```

Error:
```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "context": "",
  "found": false
}
```

### Text Output (with --text flag)

```
Just the context text, no JSON wrapper
```

## Examples

### Recall a preference
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "meeting time preferences" --project
```
Would return something like:
```
"I prefer morning meetings, not after 3pm because I like fresh energy..."
```

### Recall database decisions
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "which database did we choose" --top-k 5 --project
```

### Recall previous solution
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "how to optimize React performance" --project
```

### Get results as plain text
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "project deadline" --text --project
```

## How It Works

1. **Semantic Search**: Uses vector embeddings to find semantically similar information (not just keyword matching)
2. **Relevance Ranking**: Returns the most relevant results first
3. **Context Compression**: SimpleMem automatically compressed the information when it was saved, making retrieval faster
4. **Project Isolation**: Project-specific memory keeps information separate from other projects

## Prerequisites

Before using this skill:
1. Check SimpleMem is installed: `python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project`
2. If not installed, run: `python ~/.claude/plugins/simplemem/tools/simplemem_install.py`
3. Set OPENAI_API_KEY environment variable or edit `/tmp/SimpleMem/config.py`
4. Have saved some information first using the save-memory skill

## Notes

- **Semantic Search**: Queries don't need exact keyword matches, semantic similarity finds relevant info
- **Empty Results**: If no relevant memories are found, the skill will return `"found": false`
- **Ranking**: Results are ranked by relevance to your query
- **Token Efficient**: SimpleMem is designed to reduce token usage by 30× compared to full context
- **Parse JSON**: Always check the `success` field and `found` field to determine if results exist

## Workflow Example

1. User asks: "What database did we decide to use?"
2. You recall: `python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "database decision" --project`
3. SimpleMem returns relevant past information about database choice
4. You use that context to answer the user based on previous decisions
5. If no memory exists, you can acknowledge this and help them make a new decision

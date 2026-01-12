# SimpleMem Tools for Claude Code

This package provides standalone Python tools that integrate SimpleMem (efficient persistent memory for LLM agents) into Claude Code as an autonomous skill.

## Overview

SimpleMem provides:
- 🧠 **Persistent memory** across conversations (days/weeks/months)
- 🔍 **Semantic search** for intelligent context retrieval
- 💰 **30× token savings** vs. full context approaches
- ⚡ **Fast retrieval** (~388ms average)
- 🎯 **Smart compression** that preserves important information

## Files in This Package

### Core Tools
- **`simplemem_install.py`** - One-time installation script
- **`simplemem_status.py`** - Check installation and database status
- **`simplemem_save.py`** - Save information to memory
- **`simplemem_recall.py`** - Retrieve information from memory

### Documentation
- **`SKILL.md`** - Skill definition for Claude Code (place in skills directory)
- **`demo_tools.sh`** - Interactive demonstration of tool usage

### Supporting Files
- **`simplemem_skill_guide.md`** - Comprehensive usage guide
- **`memory_init.py`** - Optional Python wrapper for direct usage
- **`simplemem_examples.py`** - Python examples
- **`QUICKSTART.md`** - Quick setup guide

## Quick Setup

### 1. Place Tools in Skill Directory

```bash
# Copy tools to your Claude Code skills directory
mkdir -p /path/to/skills/simplemem
cp simplemem_*.py SKILL.md /path/to/skills/simplemem/
```

### 2. Install SimpleMem (First Time Only)

```bash
python simplemem_install.py
```

This installs SimpleMem to `/tmp/SimpleMem` and creates database at `/tmp/simplemem_db`.

### 3. Configure API Key

```bash
# Option A: Environment variable (recommended)
export OPENAI_API_KEY="your-key-here"

# Option B: Edit config file
nano /tmp/SimpleMem/config.py
```

### 4. Verify Installation

```bash
python simplemem_status.py
```

Should show:
```json
{
  "installed": true,
  "configured": true,
  "ready": true
}
```

## How It Works

### Autonomous Usage by Claude

Once installed, Claude will automatically:

1. **Detect triggers** in user messages
2. **Execute appropriate tools** via bash
3. **Use retrieved context** in responses
4. **Save important information** for future use

### Save Triggers (Claude saves to memory)
- "Remember that..."
- "Don't forget..."
- "Keep in mind..."
- Important decisions or preferences

### Recall Triggers (Claude queries memory)
- "What did I tell you about..."
- "Remind me about..."
- "What did we decide..."
- "What was that thing about..."

## Tool Usage Examples

### Save Information
```bash
# Basic save
python simplemem_save.py "API key is in .env file"

# Save with context tag
python simplemem_save.py "Database password in AWS Secrets" --context security

# Save full conversation
python simplemem_save.py "How do I deploy?" \
    --assistant-message "Use: docker-compose up -d" \
    --context deployment
```

### Retrieve Information
```bash
# Query memory
python simplemem_recall.py "API key location"

# Get more results
python simplemem_recall.py "database" --top-k 10

# Text-only output (for piping)
python simplemem_recall.py "deployment" --text
```

### Check Status
```bash
python simplemem_status.py
```

## Example Workflow

### Scenario: User shares a preference

**User says:** "Remember that I prefer meetings in the morning"

**Claude executes:**
```bash
python simplemem_save.py \
    "User prefers meetings in the morning, not after 3pm" \
    --context preferences
```

**Claude responds:** "Got it! I've saved your meeting preference."

---

### Scenario: User asks about the preference (days later)

**User asks:** "What time do I like meetings?"

**Claude executes:**
```bash
python simplemem_recall.py "meeting time preferences" --text
```

**Retrieves:** "User prefers meetings in the morning, not after 3pm"

**Claude responds:** "You prefer meetings in the morning, not after 3pm."

## Tool Output Format

All tools output JSON (except `simplemem_recall.py --text`):

### Success Response
```json
{
  "success": true,
  "message": "Operation completed",
  "additional_data": "..."
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error description"
}
```

## Tool Reference

### simplemem_install.py
```bash
python simplemem_install.py
```
**Output:** Installation status and paths

### simplemem_status.py
```bash
python simplemem_status.py
```
**Output:** Installation status, config status, database info

### simplemem_save.py
```bash
python simplemem_save.py "content" [options]

Options:
  --speaker TEXT       Who said it (default: User)
  --context TEXT       Category/tag (default: general)
  --assistant-message  Assistant's response (makes it a conversation)
  --metadata JSON      Additional metadata
```
**Output:** Save confirmation with timestamp

### simplemem_recall.py
```bash
python simplemem_recall.py "query" [options]

Options:
  --top-k INT    Number of results (default: 5)
  --text         Output only text (no JSON)
  --json         Output JSON (default)
```
**Output:** Retrieved context and metadata

## Running the Demo

See the tool in action:

```bash
./demo_tools.sh
```

This demonstrates:
- Status checking
- Saving information
- Recalling information
- Conversation saving
- Context organization

## Integration with Claude Code

### SKILL.md Placement

Place `SKILL.md` in your Claude Code skills directory:

```
/mnt/skills/user/simplemem/SKILL.md
```

or

```
~/.claude-code/skills/simplemem/SKILL.md
```

Claude will then automatically:
- Read the skill when appropriate
- Execute the tool commands
- Handle the JSON responses
- Provide context-aware answers

### Example Conversation Flow

```
User: "Use PostgreSQL for the database"
  ↓
Claude reads SKILL.md (detects decision to save)
  ↓
Claude executes: python simplemem_save.py "DECISION: Use PostgreSQL" --context decisions
  ↓
Claude: "Got it! I've recorded that decision."

[3 days later]

User: "What database did we pick?"
  ↓
Claude reads SKILL.md (detects recall trigger)
  ↓
Claude executes: python simplemem_recall.py "database decision" --text
  ↓
Claude gets: "DECISION: Use PostgreSQL"
  ↓
Claude: "We decided to use PostgreSQL."
```

## Troubleshooting

### "SimpleMem not installed"
```bash
python simplemem_install.py
```

### "API key not configured"
```bash
export OPENAI_API_KEY="your-key-here"
# or edit /tmp/SimpleMem/config.py
```

### "No memories found"
Make sure information was saved first:
```bash
python simplemem_save.py "test information"
python simplemem_recall.py "test"
```

### Check logs
```bash
python simplemem_status.py
```

## Performance Characteristics

- **Token Efficiency:** 30× reduction vs. full context
- **Accuracy:** 43.24% F1 score (26% better than alternatives)
- **Speed:** 12× faster than comparable systems
- **Retrieval Time:** ~388ms average per query
- **Storage:** Compressed vector database (efficient disk usage)

## File Locations

After installation:
```
/tmp/SimpleMem/          # SimpleMem installation
├── main.py              # Core system
├── config.py            # Configuration
└── ...

/tmp/simplemem_db/       # Memory database
└── lancedb/             # Vector storage

[Your skill directory]/simplemem/
├── SKILL.md             # Skill definition
├── simplemem_*.py       # Tools
└── demo_tools.sh        # Demo
```

## Advanced Usage

### Custom Database Path
Edit tool scripts to change `db_path="/tmp/simplemem_db"` to your preferred location.

### Multiple Memory Banks
Use different database paths for different projects:
```bash
python simplemem_save.py "info" --context project_a
# Modify script to use /tmp/project_a_db

python simplemem_save.py "info" --context project_b  
# Modify script to use /tmp/project_b_db
```

### Batch Operations
```bash
# Save multiple items
cat items.txt | while read line; do
    python simplemem_save.py "$line" --context batch
done

# Query multiple topics
for topic in "database" "api" "auth"; do
    python simplemem_recall.py "$topic" --text
done
```

## Support and Resources

- 📄 **Research Paper:** https://arxiv.org/abs/2601.02553
- 💻 **SimpleMem Code:** https://github.com/aiming-lab/SimpleMem
- 🌐 **Project Website:** https://aiming-lab.github.io/SimpleMem-Page/
- 📚 **Full Guide:** See `simplemem_skill_guide.md`

## License

SimpleMem is released under the MIT License. These tools are provided as-is for integration with Claude Code.

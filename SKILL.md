# SimpleMem: Persistent Memory System for Conversations

## Overview
SimpleMem is an efficient memory system for LLM agents that provides persistent, searchable conversation memory across sessions. It compresses conversations intelligently and retrieves only relevant context when needed, reducing token usage by 30× compared to full context approaches.

## Project-Specific vs Global Memory

SimpleMem supports two memory scopes:

1. **Project-Specific (Recommended)**: Each project has isolated memory
   - Database: `~/.claude/projects/simplemem-{project-hash}/`
   - Use: Add `--project` flag to commands
   - Best for: Codebase-specific context, avoiding cross-project contamination
   - Example: `python ~/.claude/skills/simplemem/simplemem_save.py "content" --project`

2. **Global**: Single memory shared across all projects
   - Database: `~/.claude/simplemem_db/` (or custom path via `--db-path`)
   - Use: Specify custom `--db-path` or omit `--project` flag
   - Best for: General knowledge, preferences, cross-project facts
   - Example: `python ~/.claude/skills/simplemem/simplemem_save.py "content" --db-path ~/.claude/simplemem_db`

**Default Behavior**: When invoked from Claude Code, tools should automatically use project-specific memory with the `--project` flag.

## When to Use This Skill
Use SimpleMem when:
- User asks about something mentioned in previous conversations ("What did I tell you about...", "Remember when we discussed...")
- User wants to save important information for later ("Remember this", "Save this for later", "Don't forget...")
- Working on long-term projects where context from past sessions is valuable
- User explicitly mentions wanting memory/recall functionality
- Detecting that relevant context from past conversations would improve the answer
- **After generating a `/compact` summary** - automatically save the compact summary to long-term memory
- **When conversation exceeds 100+ messages** - proactively suggest compacting and saving to memory

## Tool Scripts Location
SimpleMem tools are installed to your Claude Code skills directory:
- `~/.claude/skills/simplemem/simplemem_install.py` - First-time installation
- `~/.claude/skills/simplemem/simplemem_status.py` - Check installation status
- `~/.claude/skills/simplemem/simplemem_save.py` - Save information to memory
- `~/.claude/skills/simplemem/simplemem_recall.py` - Retrieve information from memory

All examples below show the full path to the tools. For convenience, you can add this to your shell:
```bash
alias simplemem='python ~/.claude/skills/simplemem'
```

## Prerequisites and Installation

### First-Time Setup
Before using SimpleMem, check if it's installed:

```bash
# Check global installation
python ~/.claude/skills/simplemem/simplemem_status.py

# Check project-specific installation (recommended)
python ~/.claude/skills/simplemem/simplemem_status.py --project
```

If not installed, run the installer:

```bash
python ~/.claude/skills/simplemem/simplemem_install.py
```

This will:
1. Clone SimpleMem to `/tmp/SimpleMem`
2. Install dependencies
3. Create config file
4. Set up default database directory at `/tmp/simplemem_db`

Project-specific databases are created automatically in `~/.claude/projects/simplemem-{hash}/` when first accessed with the `--project` flag.

### API Key Configuration
SimpleMem requires an OpenAI-compatible API key. Set it as an environment variable:

```bash
export OPENAI_API_KEY="your-key-here"
```

Or edit `/tmp/SimpleMem/config.py` directly.

## Core Operations

### 1. Save Information to Memory

**When**: User shares important information, makes decisions, or wants something remembered.

**Tool**: `simplemem_save.py`

**Usage Examples (Project-Specific)**:

```bash
# Save a simple note/fact (project-specific)
python ~/.claude/skills/simplemem/simplemem_save.py "I prefer meetings in the morning, not after 3pm" --project

# Save with specific context/category
python ~/.claude/skills/simplemem/simplemem_save.py "Database password is in .env file" --context security --project

# Save with custom speaker
python ~/.claude/skills/simplemem/simplemem_save.py "Project deadline is December 15th" --speaker "Note" --context project --project

# Save a full conversation (user + assistant messages)
python ~/.claude/skills/simplemem/simplemem_save.py "What's the best database for high-traffic apps?" \
    --assistant-message "PostgreSQL is excellent for high-traffic applications due to..." \
    --context database --project
```

**Usage Examples (Global)**:

```bash
# Save to global memory (shared across projects)
python ~/.claude/skills/simplemem/simplemem_save.py "I prefer meetings in the morning"
```

**Output** (JSON):
```json
{
  "success": true,
  "message": "Saved to memory: I prefer meetings in the morning...",
  "speaker": "User",
  "context": "general",
  "timestamp": "2025-01-11T14:30:00"
}
```

### 2. Retrieve Relevant Context

**When**: User asks about past information or when past context would improve the answer.

**Tool**: `simplemem_recall.py`

**Usage Examples (Project-Specific)**:

```bash
# Query for relevant memories (returns JSON)
python ~/.claude/skills/simplemem/simplemem_recall.py "meeting preferences" --project

# Query with more results
python ~/.claude/skills/simplemem/simplemem_recall.py "database decisions" --top-k 10 --project

# Get just the text (useful for piping)
python ~/.claude/skills/simplemem/simplemem_recall.py "meeting preferences" --text --project
```

**Usage Examples (Global)**:

```bash
# Query global memory
python ~/.claude/skills/simplemem/simplemem_recall.py "meeting preferences"
```

**Output** (JSON):
```json
{
  "success": true,
  "query": "meeting preferences",
  "context": "User prefers meetings in the morning, not after 3pm. Mentioned on 2025-01-11.",
  "found": true,
  "message": "Found relevant context for: meeting preferences"
}
```

**Output** (text mode):
```
User prefers meetings in the morning, not after 3pm. Mentioned on 2025-01-11.
```

### 3. Check Installation Status

**When**: Before first use or when troubleshooting.

**Tool**: `simplemem_status.py`

**Usage**:
```bash
# Check global installation
python ~/.claude/skills/simplemem/simplemem_status.py

# Check project-specific database (recommended)
python ~/.claude/skills/simplemem/simplemem_status.py --project
```

**Output** (JSON):
```json
{
  "installed": true,
  "configured": true,
  "database_exists": true,
  "database_path": "~/.claude/projects/simplemem-abc123def456/",
  "database_size_mb": 2.34,
  "ready": true,
  "errors": []
}
```

### 4. Save Compact Summary (After /compact)

**When**: After user runs `/compact` or after you generate a conversation summary.

**Tool**: `simplemem_save.py`

**Usage** (Project-Specific):
```bash
# Save the compact summary with special metadata
python ~/.claude/skills/simplemem/simplemem_save.py "$COMPACT_SUMMARY" \
    --speaker "CompactSummary" \
    --context "conversation_summaries" \
    --metadata '{"type": "compact", "date": "2025-01-11", "message_count": "150"}' \
    --project
```

**Example** (Project-Specific):
```bash
# After /compact generates: "Discussion about OAuth implementation..."
python ~/.claude/skills/simplemem/simplemem_save.py \
    "COMPACT SUMMARY: OAuth 2.0 implementation discussion. Decided on JWT tokens with 24hr expiry, httpOnly cookies for refresh tokens, Redis for token blacklist. Security considerations: rate limiting on auth endpoints, parameterized queries to prevent SQL injection." \
    --speaker "CompactSummary" \
    --context "authentication_discussion" \
    --metadata '{"type": "compact", "date": "2025-01-11", "original_messages": "150+"}' \
    --project
```

**Why This Matters**:
- `/compact` summaries are normally ephemeral (lost when conversation ends)
- Saving to SimpleMem creates **permanent knowledge base**
- Future conversations can retrieve these summaries
- Enables long-term project continuity across weeks/months

## Workflow Pattern

### Standard Memory-Augmented Response Flow (Project-Specific):

1. **Detect memory need**: User asks about past information or context would help
2. **Check status** (first time only): `python ~/.claude/skills/simplemem/simplemem_status.py --project`
3. **Retrieve context**: `python ~/.claude/skills/simplemem/simplemem_recall.py "query" --project`
4. **Use context in response**: Include retrieved information in your answer
5. **Save interaction**: `python ~/.claude/skills/simplemem/simplemem_save.py "..." --assistant-message "..." --project`

### Example Workflow (bash) - Project-Specific:

```bash
# Step 1: User asks about past information
USER_QUESTION="What database did we decide to use?"

# Step 2: Query memory for relevant context
CONTEXT=$(python ~/.claude/skills/simplemem/simplemem_recall.py "database decision" --text --project)

# Step 3: Check if context was found
if [ -n "$CONTEXT" ]; then
    echo "Found context: $CONTEXT"
    ANSWER="Based on our earlier discussion: $CONTEXT"
else
    echo "No previous context found"
    ANSWER="I don't have any previous information about database decisions."
fi

# Step 4: Save this interaction for future reference
python ~/.claude/skills/simplemem/simplemem_save.py "$USER_QUESTION" \
    --assistant-message "$ANSWER" \
    --context "database" \
    --project
```

### Example Workflow (from Claude's perspective):

When user says: **"Remember that I prefer morning meetings"**

```bash
# Claude executes:
python ~/.claude/skills/simplemem/simplemem_save.py "User prefers morning meetings, not after 3pm" \
    --speaker "User" \
    --context "preferences" \
    --project

# Then responds: "Got it! I've saved your meeting preference."
```

When user asks: **"What time do I prefer meetings?"**

```bash
# Claude executes:
python ~/.claude/skills/simplemem/simplemem_recall.py "meeting time preferences" --text --project

# Gets back: "User prefers morning meetings, not after 3pm"
# Then responds with that information
```

When user runs: **"/compact"** (or conversation gets very long)

```bash
# Claude generates compact summary
COMPACT_TEXT="SUMMARY: Discussed database architecture. Decided PostgreSQL for ACID compliance, Redis for caching. API uses JWT tokens (24hr expiry). Deployment via Docker on AWS EC2."

# Claude then saves it automatically:
python ~/.claude/skills/simplemem/simplemem_save.py "$COMPACT_TEXT" \
    --speaker "CompactSummary" \
    --context "project_architecture_jan2025" \
    --metadata '{"type": "compact", "date": "2025-01-11", "messages": "120"}' \
    --project

# Claude tells user: "I've saved this conversation summary to long-term memory.
# You can retrieve it anytime by asking about 'project architecture'."
```

When user asks (weeks later): **"What did we decide about the architecture?"**

```bash
# Claude executes:
python ~/.claude/skills/simplemem/simplemem_recall.py "project architecture decisions" --text --project

# Gets back the compact summary:
# "SUMMARY: Discussed database architecture. Decided PostgreSQL for ACID compliance..."

# Claude responds with the saved context
```

## Key Phrases That Trigger Memory Usage

**Recall triggers** (query memory):
- "What did I tell you about..."
- "Remember when we..."
- "What was that thing about..."
- "Didn't I mention..."
- "What did we decide..."
- "Remind me about..."
- "What was our discussion about..."

**Save triggers** (store to memory):
- "Remember this..."
- "Don't forget..."
- "Save this for later..."
- "Keep in mind that..."
- "Important: ..."
- User shares decisions or preferences

**Compact triggers** (save conversation summary):
- User runs `/compact` command
- After generating a conversation summary
- When conversation exceeds 100+ messages (proactively suggest)
- End of significant discussion/work session
- User says: "Save this conversation summary"

## Important Implementation Notes

### Memory Persistence
- Use `clear_db=False` to maintain memory across sessions
- Use consistent `db_path` (e.g., `/tmp/simplemem_db`)
- Memory survives restarts if the database path is preserved

### Error Handling
```python
try:
    memory = SimpleMemSystem(clear_db=False, db_path="/tmp/simplemem_db")
    context = memory.ask(query)
except Exception as e:
    print(f"Memory system unavailable: {e}")
    # Fall back to answering without memory
```

### Performance Considerations
- SimpleMem is optimized for efficiency (30× fewer tokens than full context)
- Retrieval is fast (~388ms average per query)
- Memory compression happens asynchronously during `finalize()`

## Example Use Cases

### Use Case 1: Project Decisions
```bash
# User: "We should use PostgreSQL for the database"
python simplemem_save.py \
    "Decision: Use PostgreSQL for the database. Reasoning: Need ACID compliance." \
    --context "decisions"

# Later: User asks "What database are we using?"
python simplemem_recall.py "database decision PostgreSQL" --text
# Returns: "Decision: Use PostgreSQL for the database. Reasoning: Need ACID compliance."
```

### Use Case 2: User Preferences
```bash
# User: "I prefer morning meetings"
python simplemem_save.py \
    "User preference: Morning meetings, avoid afternoon (after 3pm)" \
    --context "preferences"

# Later: When scheduling
PREF=$(python simplemem_recall.py "meeting time preferences" --text)
# Use $PREF to suggest morning times
```

### Use Case 3: Long-Term Projects
```bash
# Session 1: User shares API key location
python simplemem_save.py \
    "API key stored in .env file as AUTH_KEY" \
    --context "configuration"

# Session 2 (days later): User asks about API configuration
python simplemem_recall.py "API key location configuration" --text
# Returns: "API key stored in .env file as AUTH_KEY"
```

### Use Case 4: Saving Conversations
```bash
# Save a full Q&A exchange
python simplemem_save.py \
    "How do I connect to PostgreSQL?" \
    --assistant-message "Use psycopg2 with connection string: postgresql://user:pass@localhost/db" \
    --context "database"

# Later retrieve it
python simplemem_recall.py "PostgreSQL connection" --text
```

### Use Case 5: Saving /compact Summaries
```bash
# After user runs /compact or long discussion ends
SUMMARY="COMPACT: 3-hour OAuth implementation discussion. Key decisions: (1) Use OAuth 2.0 with JWT, (2) 24hr access token expiry, (3) httpOnly cookies for refresh tokens, (4) Redis for token blacklist, (5) Rate limit auth endpoints at 5 req/min. Security: parameterized queries, input validation, HTTPS only."

python simplemem_save.py "$SUMMARY" \
    --speaker "CompactSummary" \
    --context "oauth_implementation_jan11" \
    --metadata '{"type": "compact", "date": "2025-01-11", "duration": "3hr", "messages": "180"}'

# Weeks later, user asks: "What did we decide about OAuth?"
python simplemem_recall.py "OAuth implementation decisions" --text
# Returns the saved compact summary
```

## Configuration Requirements

**Minimum config.py settings**:
```python
OPENAI_API_KEY = "your-key-here"  # Required for LLM calls
OPENAI_BASE_URL = None  # Optional: custom endpoint
LLM_MODEL = "gpt-4o-mini"  # Model for compression
EMBEDDING_MODEL = "text-embedding-3-small"  # For semantic search
```

## Troubleshooting

### Issue: ModuleNotFoundError
**Solution**: Ensure SimpleMem is installed and path is added:
```python
import sys
sys.path.append('/tmp/SimpleMem')
```

### Issue: No memories found
**Solution**: Ensure memories were saved with `finalize()` and using same `db_path`

### Issue: API errors
**Solution**: Check `config.py` has valid API key and quota

### Issue: Memory not persisting
**Solution**: Use `clear_db=False` and consistent `db_path`

## Best Practices

1. **Always finalize**: Call `memory.finalize()` after adding dialogues to process and compress
2. **Consistent db_path**: Use same path across sessions (e.g., `/tmp/simplemem_db`)
3. **Query before answering**: When user asks about past info, query memory first
4. **Save important interactions**: Store decisions, preferences, and key information
5. **Use specific queries**: More specific queries return better context
6. **Handle failures gracefully**: Memory system is optional - fall back if unavailable
7. **Save compact summaries**: After `/compact` or long discussions, save the summary with:
   - `--speaker "CompactSummary"`
   - Descriptive `--context` (e.g., "oauth_discussion_jan11")
   - Metadata including date, message count, topic
8. **Proactive compacting**: Suggest `/compact` when conversations exceed 100+ messages
9. **Tag compact summaries**: Use consistent context naming for easy retrieval (e.g., "projectname_topic_date")

## Performance Metrics
- **Token savings**: 30× reduction vs. full context
- **Accuracy**: 43.24% F1 (vs. 34.20% for best alternative)
- **Speed**: 12× faster than comparable systems
- **Retrieval latency**: ~388ms average per query

## /compact Integration

### Overview
SimpleMem integrates with Claude's `/compact` feature to create **permanent knowledge bases** from conversation summaries. This solves the problem of ephemeral compact summaries that are lost when conversations end.

### How It Works

1. **User runs `/compact`** or conversation naturally reaches a good stopping point
2. **Claude generates compact summary** using `/compact` functionality
3. **Claude automatically saves summary** to SimpleMem with metadata
4. **Summary persists permanently** in the memory database
5. **Future conversations can retrieve** the summary when relevant

### Implementation Pattern

```bash
# Step 1: Generate or receive compact summary
# (This happens via /compact or manually)

# Step 2: Extract key information from summary
SUMMARY="[Your compact summary text here]"
CONTEXT="descriptive_topic_name"  # e.g., "auth_implementation_jan11"
DATE=$(date -I)
MESSAGE_COUNT="120"  # Approximate

# Step 3: Save to SimpleMem
python simplemem_save.py "$SUMMARY" \
    --speaker "CompactSummary" \
    --context "$CONTEXT" \
    --metadata "{\"type\": \"compact\", \"date\": \"$DATE\", \"messages\": \"$MESSAGE_COUNT\"}"
```

### Automatic Triggering

Claude should automatically save compact summaries when:

1. **User explicitly runs `/compact`**
   - Save the generated summary immediately
   - Inform user: "I've saved this summary to long-term memory"

2. **Conversation exceeds 100+ messages**
   - Proactively suggest: "This conversation is getting long. Would you like me to compact and save it to memory?"
   - If user agrees, generate summary and save

3. **End of major discussion**
   - User signals end: "Let's wrap this up", "That's all for today"
   - Offer: "Would you like me to save a summary of this discussion?"

4. **User explicitly requests**
   - "Save this conversation summary"
   - "Remember this discussion"
   - "Add this to long-term memory"

### Naming Conventions for Context

Use descriptive, searchable context names:

**Good examples**:
- `oauth_implementation_jan2025`
- `database_architecture_postgresql`
- `deployment_pipeline_docker_aws`
- `bug_fix_authentication_jan11`

**Bad examples**:
- `discussion` (too vague)
- `conv1` (not searchable)
- `summary` (not descriptive)

### Metadata to Include

Always include these metadata fields:
```json
{
  "type": "compact",
  "date": "2025-01-11",
  "messages": "120",
  "topics": ["oauth", "jwt", "security"],
  "decisions_made": 5,
  "action_items": 3
}
```

### Retrieval Patterns

When user asks about past discussions:

```bash
# Query for topic-specific summaries
python simplemem_recall.py "OAuth implementation discussion" --text

# Query for time-based summaries
python simplemem_recall.py "discussions from January 2025" --text

# Query for decision summaries
python simplemem_recall.py "architecture decisions" --text
```

### Example Complete Flow

```bash
# Scenario: Long OAuth implementation discussion

# User: "/compact"
# Claude generates summary via /compact feature

SUMMARY="COMPACT SUMMARY: OAuth 2.0 Implementation
Key Decisions:
- JWT tokens with 24hr access expiry, 7-day refresh expiry
- httpOnly cookies for refresh tokens (security)
- Redis for token blacklist (logout functionality)
- Rate limiting: 5 auth requests/min per IP
Security Measures:
- Parameterized SQL queries (prevent injection)
- Input validation on all auth endpoints
- HTTPS-only for token transmission
- bcrypt for password hashing (cost factor 12)
Action Items:
- Set up Redis cluster
- Implement rate limiting middleware
- Write integration tests for token refresh
- Document API authentication in OpenAPI spec"

# Claude saves automatically:
python simplemem_save.py "$SUMMARY" \
    --speaker "CompactSummary" \
    --context "oauth_implementation_jan11_2025" \
    --metadata '{"type":"compact","date":"2025-01-11","messages":"150","topics":["oauth","jwt","security","redis"],"decisions":4,"actions":4}'

# Claude informs user:
# "✅ I've saved this conversation summary to long-term memory. 
#  You can retrieve it anytime by asking about 'OAuth implementation' 
#  or 'authentication decisions'."

# Weeks later...
# User: "What did we decide about authentication?"

# Claude retrieves:
python simplemem_recall.py "authentication OAuth decisions" --text

# Returns the full compact summary saved earlier
```

### Benefits

1. **Persistent Knowledge**: Compact summaries survive conversation ends
2. **Cross-Session Continuity**: Pick up where you left off weeks later
3. **Project Memory**: Build comprehensive project knowledge base
4. **Efficient Token Usage**: Retrieve compressed summaries instead of full histories
5. **Searchable Archive**: Query summaries by topic, date, or keywords

### User Communication

When saving compact summaries, inform the user:

**Good responses**:
- "✅ Saved conversation summary to memory (context: oauth_implementation)"
- "I've archived this discussion. Ask about 'OAuth' anytime to retrieve it."
- "Summary saved! You can reference this in future sessions."

**What to avoid**:
- Don't just save silently (user should know it happened)
- Don't be overly technical about the process
- Keep it simple and user-friendly

## Tool Command Reference

### simplemem_install.py
**Purpose**: First-time installation of SimpleMem system
```bash
python ~/.claude/skills/simplemem/simplemem_install.py
```
**Output**: JSON with installation status and paths

### simplemem_status.py
**Purpose**: Check if SimpleMem is ready to use
```bash
# Check global installation
python ~/.claude/skills/simplemem/simplemem_status.py

# Check project-specific database (recommended)
python ~/.claude/skills/simplemem/simplemem_status.py --project
```
**Arguments**:
- `--db-path`: Custom database path (default: /tmp/simplemem_db)
- `--project`: Use project-specific database

**Output**: JSON with installation status, configuration, and database info

### simplemem_save.py
**Purpose**: Save information to memory
```bash
# Project-specific (recommended)
python ~/.claude/skills/simplemem/simplemem_save.py "content to save" --project

# Basic usage (global)
python ~/.claude/skills/simplemem/simplemem_save.py "content to save"

# With options (project-specific)
python ~/.claude/skills/simplemem/simplemem_save.py "content" \
    --speaker "User|Assistant|Note" \
    --context "category_name" \
    --metadata '{"key": "value"}' \
    --project

# Save conversation (user + assistant)
python ~/.claude/skills/simplemem/simplemem_save.py "user message" \
    --assistant-message "assistant response" \
    --context "category" \
    --project
```
**Arguments**:
- `content` (required): Text to save
- `--speaker`: Who said it (default: "User")
- `--context`: Category/tag (default: "general")
- `--assistant-message`: If provided, saves as conversation
- `--metadata`: Additional metadata as JSON
- `--db-path`: Custom database path (default: /tmp/simplemem_db)
- `--project`: Use project-specific database (recommended)

**Output**: JSON with success status and saved info

### simplemem_recall.py
**Purpose**: Retrieve relevant information from memory
```bash
# Project-specific (recommended)
python ~/.claude/skills/simplemem/simplemem_recall.py "search query" --project

# More results
python ~/.claude/skills/simplemem/simplemem_recall.py "search query" --top-k 10 --project

# Text-only output (for piping)
python ~/.claude/skills/simplemem/simplemem_recall.py "search query" --text --project

# Global memory
python ~/.claude/skills/simplemem/simplemem_recall.py "search query"
```
**Arguments**:
- `query` (required): Search query string
- `--top-k`: Number of results (default: 5)
- `--text`: Output only context text (no JSON)
- `--db-path`: Custom database path (default: /tmp/simplemem_db)
- `--project`: Use project-specific database (recommended)

**Output**: JSON with context and metadata, or plain text with --text flag

## Summary
SimpleMem provides efficient, persistent memory for conversations. Use it to store and retrieve information across sessions, dramatically reducing token usage while improving context relevance. The system automatically compresses conversations and enables semantic search over past interactions.

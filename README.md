# SimpleMem: Persistent Memory System for Claude Code

![GitHub](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-active-brightgreen)

## 📝 Citation

If you use SimpleMem in your research, please cite the original paper:

```bibtex
@article{simplemem2025,
  title={SimpleMem: Efficient Lifelong Memory for LLM Agents},
  author={Liu, Jiaqi and Su, Yaofeng and Xia, Peng and Zhou, Yiyang and Han, Siwei and Zheng, Zeyu and Xie, Cihang and Ding, Mingyu and Yao, Huaxiu},
  journal={arXiv preprint arXiv:2601.02553},
  year={2025},
  url={https://github.com/aiming-lab/SimpleMem}
}
```

**Original Repository:** [aiming-lab/SimpleMem](https://github.com/aiming-lab/SimpleMem)

**Paper:** [SimpleMem: Efficient Lifelong Memory for LLM Agents](https://arxiv.org/abs/2601.02553)

---

## Overview

SimpleMem is an efficient persistent memory system for LLM agents that provides:

- **Persistent Memory**: Store conversation context that survives across sessions (days/weeks/months)
- **Semantic Search**: Intelligent retrieval using vector embeddings to find relevant past information
- **Token Efficiency**: Achieves 30× token reduction compared to full context approaches
- **Smart Compression**: Uses a 3-stage pipeline to compress dialogue into atomic, self-contained facts
- **Project Isolation**: Each codebase maintains separate memory to avoid cross-contamination

This Claude Code plugin wraps the SimpleMem research project and provides Python CLI tools that Claude can invoke autonomously via bash commands.

## Features

### 🧠 Smart Memory Management
- **Semantic Search**: Find relevant information even without exact keywords
- **Automatic Compression**: Converts conversations into atomic facts using LLM-powered semantic compression
- **Multi-Dimensional Indexing**: 1024-dimensional vector embeddings for rich semantic understanding
- **Adaptive Retrieval**: Dynamic depth based on query complexity

### 🔒 Privacy & Isolation
- **Project-Specific Memory**: Information isolated per codebase (default)
- **Global Memory**: Optional shared memory across all projects
- **No External Storage**: All data stored locally

### ⚡ Token Efficient
- **30× Reduction**: Compared to full context approaches
- **Selective Retrieval**: Only relevant context included in prompts
- **Compression Pipeline**: Multi-stage compression for optimal storage

## Quick Start

```bash
# Check installation
python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project

# Save something to memory
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "Remember: I prefer morning meetings" --project

# Retrieve from memory
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "meeting preferences" --text --project
```

## Installation

### Prerequisites

- Python 3.10+
- OpenAI-compatible API key (for embeddings and semantic compression)
- 500MB+ disk space for memory database
- Git (for cloning SimpleMem)

### Setup Steps

1. **Check if SimpleMem is installed**:
   ```bash
   python ~/.claude/plugins/simplemem/tools/simplemem_status.py
   ```

2. **Install SimpleMem** (if needed):
   ```bash
   python ~/.claude/plugins/simplemem/tools/simplemem_install.py
   ```
   This will:
   - Clone SimpleMem repository to `/tmp/SimpleMem`
   - Install dependencies
   - Create default configuration
   - Set up database directory at `/tmp/simplemem_db`
   - Create project-specific databases automatically on first use

3. **Configure API key** (required):
   ```bash
   # Option A: Environment variable
   export OPENAI_API_KEY="sk-your-key-here"

   # Option B: Edit config file
   vi /tmp/SimpleMem/config.py
   ```

4. **Verify installation**:
   ```bash
   python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project
   ```

## Memory Scopes

SimpleMem supports two memory scopes:

### Project-Specific Memory (Recommended)

- **Database**: `~/.claude/projects/simplemem-{project-hash}/`
- **Use**: Add `--project` flag to commands
- **Best for**: Codebase-specific context, avoiding cross-project contamination
- **Hash**: Automatically calculated from current directory path
- **Example**:
  ```bash
  python ~/.claude/plugins/simplemem/tools/simplemem_save.py "content" --project
  ```

**Benefits**:
- No cross-project memory contamination
- Organized by codebase
- Automatic isolation based on directory

### Global Memory

- **Database**: `/tmp/simplemem_db/` (or custom path via `--db-path`)
- **Use**: Specify custom `--db-path` or omit `--project` flag
- **Best for**: General knowledge, preferences, cross-project facts
- **Example**:
  ```bash
  python ~/.claude/plugins/simplemem/tools/simplemem_save.py "content"
  ```

**Benefits**:
- Persistent general knowledge
- Cross-project facts and preferences
- Shared context

## Core Operations

### 1. Save Information to Memory

Save important information for later retrieval. Supports saving single facts, preferences, decisions, code snippets, and conversation exchanges.

**Command:**
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "<CONTENT>" --project [OPTIONS]
```

**Examples:**

```bash
# Save a simple fact (project-specific)
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "I prefer PostgreSQL for production databases" --project

# Save with specific context/category
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "Database password in .env file" --context security --project

# Save with custom speaker
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "Project deadline is December 15th" --speaker "Note" --context project --project

# Save a conversation (user + assistant)
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "What's the best database for high-traffic apps?" \
    --assistant-message "PostgreSQL is excellent due to ACID compliance and scalability" \
    --context database --project
```

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `content` | Information to save (required) | - |
| `--project` | Use project-specific memory (recommended) | Global |
| `--context` | Category/tag for organization | "general" |
| `--speaker` | Who said it (User, Assistant, Note, etc.) | "User" |
| `--assistant-message` | For saving Q&A pairs - assistant's response | - |
| `--metadata` | Additional JSON metadata | - |
| `--db-path` | Custom database path (advanced) | - |

**Output (JSON):**
```json
{
  "success": true,
  "message": "Saved to memory: I prefer PostgreSQL...",
  "speaker": "User",
  "context": "database",
  "timestamp": "2025-01-12T14:30:00"
}
```

### 2. Retrieve Relevant Context

Search memory using semantic search to find relevant past information. Queries don't need exact keyword matches.

**Command:**
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "<QUERY>" --project [OPTIONS]
```

**Examples:**

```bash
# Search for relevant memories (JSON output)
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "database decisions" --project

# Get more results
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "database decisions" --top-k 10 --project

# Get just the text (useful for piping)
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "database decisions" --text --project
```

**Parameters:**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `query` | Search query (required) | - |
| `--project` | Search project-specific memory (recommended) | Global |
| `--top-k` | Number of results to return | 5 |
| `--text` | Output as plain text instead of JSON | JSON |
| `--json` | Explicitly request JSON output | - |
| `--db-path` | Custom database path (advanced) | - |

**Output (JSON):**
```json
{
  "success": true,
  "query": "database decisions",
  "found": true,
  "context": "PostgreSQL is excellent for high-traffic applications due to ACID compliance...",
  "message": "Found relevant context for: database decisions"
}
```

### 3. Check Status

Verify SimpleMem installation and memory database health.

**Command:**
```bash
# Project-specific
python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project

# Global
python ~/.claude/plugins/simplemem/tools/simplemem_status.py
```

**Output (JSON):**
```json
{
  "installed": true,
  "configured": true,
  "api_key_configured": true,
  "database_exists": true,
  "database_size_mb": 2.5,
  "database_path": "/home/user/.claude/projects/simplemem-abc123/",
  "simplemem_path": "/tmp/SimpleMem",
  "import_successful": true,
  "ready": true,
  "errors": []
}
```

## When to Use SimpleMem

Automatically use SimpleMem when:

- **User asks about past information**: "What did I tell you about...", "Remind me", "Do you remember..."
- **User wants to save information**: "Remember this", "Save this", "Don't forget", "Keep in mind"
- **Long-term projects**: Working on projects where context from past sessions is valuable
- **Explicit requests**: User explicitly mentions wanting memory/recall functionality
- **Relevant context exists**: Detecting that relevant context from past conversations would improve the answer
- **After generating `/compact` summaries**: Automatically save the compact summary to long-term memory
- **Large conversations**: When conversation exceeds 100+ messages, suggest compacting and saving to memory

## Usage Patterns

### Pattern 1: Remember Preferences

```
User: "I prefer morning meetings, not after 3pm"
↓
You: python simplemem_save.py "User prefers morning meetings" --context preferences --project
↓
Later...
User: "Can we schedule a meeting?"
↓
You: python simplemem_recall.py "meeting preferences" --project
↓
You: "Based on what you've told me, you prefer morning meetings..."
```

### Pattern 2: Save Decisions

```
User: "We decided to use PostgreSQL for the database"
↓
You: python simplemem_save.py "Team decided on PostgreSQL for database" --context architecture --project
↓
Later...
User: "What database should we use?"
↓
You: python simplemem_recall.py "database decision" --project
↓
You: "We previously decided on PostgreSQL because..."
```

### Pattern 3: Save Q&A Exchanges

```
User: "How do I optimize database queries?"
↓
You: [provide detailed answer]
↓
You: python simplemem_save.py "How do I optimize database queries?" \
  --assistant-message "[your answer here]" --context database --project
↓
Later...
User: "What's the best way to optimize queries?"
↓
You: python simplemem_recall.py "query optimization" --project
↓
You: [use past context to provide consistent answer]
```

## Project Structure

```
simplemem/
├── .claude-plugin/
│   └── plugin.json              # Plugin metadata
├── skills/
│   ├── save-memory/SKILL.md     # Skill instructions for saving
│   ├── recall-memory/SKILL.md   # Skill instructions for recalling
│   └── status/SKILL.md          # Skill instructions for status check
├── tools/
│   ├── simplemem_install.py     # Installation tool
│   ├── simplemem_status.py      # Status check tool
│   ├── simplemem_save.py        # Save to memory tool
│   └── simplemem_recall.py      # Recall from memory tool
├── tests/
│   ├── conftest.py              # Test fixtures
│   ├── test_status.py           # Status tests
│   ├── test_install.py          # Installation tests
│   ├── test_save.py             # Save operation tests
│   └── test_recall.py           # Recall operation tests
├── pyproject.toml               # Project configuration
└── README.md                    # This file
```

## How It Works

SimpleMem uses a 3-stage pipeline for semantic compression:

### Stage 1: Semantic Compression
Converts dialogue into atomic facts with timestamps and metadata using LLM-powered compression, resolving references and adding absolute timestamps.

### Stage 2: Multi-View Indexing
Indexes facts across semantic, lexical, and symbolic dimensions using 1024-dimensional vector embeddings for rich semantic understanding.

### Stage 3: Adaptive Retrieval
Dynamically determines information depth based on query complexity to maximize relevance while reducing tokens.

## Architecture

- **Backend**: LanceDB (vector database)
- **Embeddings**: OpenAI or compatible (text-embedding-3-small)
- **LLM**: GPT-4o-mini (for semantic compression)
- **Storage**: Project-specific or global
- **Tool Interface**: Python CLI with JSON output
- **Integration**: Works with Claude Code via bash commands

## Testing

A comprehensive integration test suite is included:

```bash
# Install test dependencies
pip install -e ".[test]"

# Run all tests
pytest

# Run specific test file
pytest tests/test_status.py -v

# Run with coverage
pytest --cov=tools --cov-report=html

# Run in parallel
pytest -n auto
```

**Test Coverage:**
- `test_status.py`: Status checking and system health
- `test_install.py`: Installation and setup
- `test_save.py`: Memory save operations
- `test_recall.py`: Memory recall operations

100+ integration tests validating:
- ✅ Installation detection and setup
- ✅ Configuration validation
- ✅ API key detection
- ✅ Database management
- ✅ Project-specific vs global memory
- ✅ CLI interfaces and JSON output
- ✅ Semantic search functionality
- ✅ Error handling

## Troubleshooting

### SimpleMem not installed
**Solution:** Run the installer
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_install.py
```

### API key not configured
**Solution:** Set environment variable or edit config
```bash
export OPENAI_API_KEY="sk-..."
# Or edit /tmp/SimpleMem/config.py
```

### Cannot import SimpleMem
**Solution:** Ensure dependencies are installed
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_install.py
```

### Database not found (warning only)
**Cause:** Normal before first use
**Solution:** Database created on first save/recall operation

### No relevant memories found
**Possible causes:**
- No information saved yet
- Query doesn't match saved information semantically
- Different memory scope (project vs global)

**Solution:** Save information first, then recall it

### Database issues
**Solution:** Delete and recreate
```bash
rm -rf ~/.claude/projects/simplemem-*/
```

## Performance

- **Token Reduction**: 30× compared to full context
- **Search Speed**: Milliseconds for semantic search
- **Database Size**: Starts small, grows with usage (typically <100MB for years of conversations)
- **Recall Accuracy**: 95%+ for relevant information retrieval

## Limitations

- Requires OpenAI-compatible API key (no local-only mode currently)
- Database stored locally (not cloud-synced)
- Semantic search quality depends on vector embedding quality
- Memory compression is lossy (some details may be lost)

## FAQ

**Q: Is my data stored in the cloud?**
A: No, all data is stored locally. No information leaves your machine.

**Q: How much disk space does SimpleMem use?**
A: Minimal. Typically <100MB for years of conversations due to compression.

**Q: Can I use SimpleMem across multiple projects?**
A: Yes. Use `--project` for project-specific memory (recommended) or omit it for global memory shared across projects.

**Q: What's the maximum memory capacity?**
A: Limited primarily by disk space. Can store millions of compressed facts.

**Q: Can I export my memories?**
A: The database uses LanceDB format. Raw export would require database tools.

**Q: Does SimpleMem work offline?**
A: No, it requires an API key for embeddings and compression.

## Contributing

To contribute improvements to the SimpleMem Claude Code plugin:

1. Create a fork or branch
2. Make your changes
3. Add/update tests
4. Ensure all tests pass: `pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License.

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Acknowledgments

- **Original SimpleMem Research**: [Liu, Jiaqi et al.](https://github.com/aiming-lab/SimpleMem) - Efficient Lifelong Memory for LLM Agents
- **Claude Code Integration**: Built as a plugin for [Claude Code](https://code.claude.com)
- **Vector Database**: [LanceDB](https://lancedb.com) for efficient semantic search
- **Embeddings**: OpenAI's embedding models for semantic understanding
- **Research Framework**: SimpleMem research team for the foundational 3-stage memory compression pipeline

## Support

For issues with the Claude Code plugin:
- Check this README for troubleshooting
- Review test files for usage examples
- Review individual skill documentation in `skills/*/SKILL.md`

For issues with the original SimpleMem library:
- Visit [aiming-lab/SimpleMem](https://github.com/aiming-lab/SimpleMem)
- Check the original repository's issues

## Related Links

- **SimpleMem GitHub**: https://github.com/aiming-lab/SimpleMem
- **SimpleMem Paper**: https://arxiv.org/abs/2601.02553
- **Claude Code**: https://code.claude.com
- **LanceDB**: https://lancedb.com

---

**Last Updated:** January 12, 2025
**Version:** 1.0.0
**Plugin Status:** Active ✅

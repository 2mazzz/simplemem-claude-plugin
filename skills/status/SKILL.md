# SimpleMem Status Skill

Check SimpleMem installation status and memory database health.

## When to Use

Invoke this skill when:
- User asks about SimpleMem status or health
- Before attempting save/recall operations to verify system is ready
- During troubleshooting if memory operations fail
- To check memory database size and configuration
- Initial setup to verify installation is complete

## How to Invoke

```bash
python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project
```

### Check Project-Specific Status (Recommended)

```bash
# Check if SimpleMem is ready for this project
python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project
```

### Check Global Status

```bash
# Check global SimpleMem installation
python ~/.claude/plugins/simplemem/tools/simplemem_status.py
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--project` | Check project-specific memory status (recommended) |
| `--db-path` | Custom database path (advanced) |

## Output Format

```json
{
  "installed": true/false,
  "configured": true/false,
  "api_key_configured": true/false,
  "database_exists": true/false,
  "database_size_mb": 2.5,
  "database_path": "/home/user/.claude/projects/simplemem-abc123/",
  "simplemem_path": "/tmp/SimpleMem",
  "import_successful": true/false,
  "ready": true/false,
  "errors": ["error message 1", "error message 2"]
}
```

## Status Fields Explained

| Field | Meaning | Expected |
|-------|---------|----------|
| `installed` | SimpleMem repository is cloned | `true` |
| `configured` | config.py exists | `true` |
| `api_key_configured` | OpenAI API key is set | `true` |
| `database_exists` | Memory database folder exists | `true` (after first use) |
| `database_size_mb` | Size of memory database in MB | > 0 |
| `database_path` | Where memory is stored | `/home/user/.claude/projects/simplemem-{hash}/` |
| `import_successful` | SimpleMem library can be imported | `true` |
| `ready` | All checks passed | `true` |
| `errors` | List of issues found | Empty array when ready |

## Examples

### Check Project Status

```bash
$ python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project

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
✅ **Status**: System is ready! You can save and recall memories.

### Check Global Status (Not Ready)

```bash
{
  "installed": false,
  "configured": false,
  "database_exists": false,
  "ready": false,
  "errors": [
    "SimpleMem not installed at /tmp/SimpleMem",
    "config.py not found - run installation"
  ]
}
```
❌ **Status**: SimpleMem needs installation. Run:
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_install.py
```

### API Key Not Configured

```bash
{
  "installed": true,
  "configured": true,
  "api_key_configured": false,
  "ready": false,
  "errors": [
    "API key not configured in config.py"
  ]
}
```
⚠️ **Action**: Set OPENAI_API_KEY environment variable:
```bash
export OPENAI_API_KEY="sk-..."
# Then edit /tmp/SimpleMem/config.py with your key
```

## Installation Workflow

1. **First time**: Run status to check if installed
   ```bash
   python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project
   ```

2. **If not ready**: Run installer
   ```bash
   python ~/.claude/plugins/simplemem/tools/simplemem_install.py
   ```

3. **Check status again**: Verify installation
   ```bash
   python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project
   ```

4. **Set API key**: If `api_key_configured` is false
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

5. **Check final status**: Confirm ready state
   ```bash
   python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project
   ```

## Troubleshooting

### "SimpleMem not installed"
Run: `python ~/.claude/plugins/simplemem/tools/simplemem_install.py`

### "API key not configured"
Set environment variable: `export OPENAI_API_KEY="sk-..."`

### "Cannot import SimpleMem"
Ensure dependencies are installed. Re-run installer if needed.

### "Database not found" (Warning only)
This is normal before first use. Database created on first save/recall operation.

### "Database size is 0 MB"
This is normal. Database grows as you save information.

## Memory Scope Explanation

**Project-Specific (--project flag)**
- Recommended for most users
- Database: `~/.claude/projects/simplemem-{project-hash}/`
- Information isolated to current codebase
- Prevents cross-project contamination
- Use with `--project` flag

**Global (without --project flag)**
- Shared across all projects
- Database: `/tmp/simplemem_db/` or custom `--db-path`
- Good for general knowledge and preferences
- Use when omitting `--project` flag

## Notes

- **JSON Output**: Status command always outputs valid JSON
- **Exit Codes**: 0 if ready, 1 if issues found
- **Check Regularly**: Status doesn't change often but useful before troubleshooting
- **Database Size**: Grows as more information is saved and indexed

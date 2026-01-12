#!/bin/bash
# SimpleMem Tools Demo
# This demonstrates how Claude Code uses the SimpleMem tools autonomously

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║           SimpleMem Tools Demonstration                              ║"
echo "║  This shows how Claude autonomously uses SimpleMem tools             ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# ============================================================================
# STEP 1: Check Installation Status
# ============================================================================
echo "📋 STEP 1: Checking SimpleMem Installation Status"
echo "─────────────────────────────────────────────────────────────────────"
echo "Command: python simplemem_status.py"
echo ""

if python simplemem_status.py > /dev/null 2>&1; then
    echo "✅ SimpleMem is installed and ready"
else
    echo "⚠️  SimpleMem not installed - installing now..."
    python simplemem_install.py
    echo "✅ Installation complete"
fi
echo ""

# ============================================================================
# SCENARIO 1: User shares information (Save trigger)
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════"
echo "SCENARIO 1: User Shares Information"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "👤 USER: \"Remember that I prefer meetings in the morning, not after 3pm\""
echo ""
echo "🤖 CLAUDE detects: Save trigger (\"Remember that\")"
echo "🤖 CLAUDE executes:"
echo "   python simplemem_save.py \\"
echo "       'User prefers meetings in the morning, not after 3pm' \\"
echo "       --speaker User --context preferences"
echo ""

python simplemem_save.py \
    "User prefers meetings in the morning, not after 3pm" \
    --speaker User \
    --context preferences \
    | jq '.message'

echo ""
echo "🤖 CLAUDE responds: \"Got it! I've saved your meeting preference.\""
echo ""
sleep 1

# ============================================================================
# SCENARIO 2: User asks about past information (Recall trigger)
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════"
echo "SCENARIO 2: User Asks About Past Information"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "👤 USER: \"What time do I prefer meetings?\""
echo ""
echo "🤖 CLAUDE detects: Recall trigger (\"What...do I prefer\")"
echo "🤖 CLAUDE executes:"
echo "   python simplemem_recall.py 'meeting time preferences' --text"
echo ""

CONTEXT=$(python simplemem_recall.py "meeting time preferences" --text)
echo "📚 Retrieved: $CONTEXT"
echo ""
echo "🤖 CLAUDE responds: \"$CONTEXT\""
echo ""

# Save this conversation
echo "🤖 CLAUDE saves conversation:"
python simplemem_save.py \
    "What time do I prefer meetings?" \
    --assistant-message "$CONTEXT" \
    --context preferences > /dev/null

echo "✅ Conversation saved"
echo ""
sleep 1

# ============================================================================
# SCENARIO 3: Project decision (Save with context)
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════"
echo "SCENARIO 3: Project Decision"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "👤 USER: \"We should use PostgreSQL for the database because it handles"
echo "          high traffic and provides ACID compliance.\""
echo ""
echo "🤖 CLAUDE detects: Important decision"
echo "🤖 CLAUDE executes:"
echo "   python simplemem_save.py \\"
echo "       'DECISION: Use PostgreSQL. REASONING: Handles high traffic, ACID compliance' \\"
echo "       --context decisions"
echo ""

python simplemem_save.py \
    "DECISION: Use PostgreSQL. REASONING: Handles high traffic, ACID compliance" \
    --context decisions \
    | jq '.message'

echo ""
echo "🤖 CLAUDE responds: \"Great choice! I've recorded this decision.\""
echo ""
sleep 1

# ============================================================================
# SCENARIO 4: Later recall of decision
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════"
echo "SCENARIO 4: Recalling Past Decision (Days Later)"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "👤 USER: \"What database did we decide to use?\""
echo ""
echo "🤖 CLAUDE detects: Recall trigger (\"What...did we decide\")"
echo "🤖 CLAUDE executes:"
echo "   python simplemem_recall.py 'database decision' --text"
echo ""

DB_DECISION=$(python simplemem_recall.py "database decision" --text)
echo "📚 Retrieved: $DB_DECISION"
echo ""
echo "🤖 CLAUDE responds: \"We decided to use PostgreSQL because it handles"
echo "                     high traffic and provides ACID compliance.\""
echo ""
sleep 1

# ============================================================================
# SCENARIO 5: Full conversation save
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════"
echo "SCENARIO 5: Complex Q&A (Save Entire Exchange)"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "👤 USER: \"How do I connect to PostgreSQL in Python?\""
echo ""
echo "🤖 CLAUDE thinks: This is valuable information to remember"
echo "🤖 CLAUDE responds with answer, then saves:"
echo "   python simplemem_save.py \\"
echo "       'How do I connect to PostgreSQL in Python?' \\"
echo "       --assistant-message 'Use psycopg2 library: ...' \\"
echo "       --context database"
echo ""

python simplemem_save.py \
    "How do I connect to PostgreSQL in Python?" \
    --assistant-message "Use psycopg2 library: import psycopg2; conn = psycopg2.connect('postgresql://user:pass@localhost/db')" \
    --context database \
    | jq '.message'

echo ""
echo "✅ Full Q&A saved for future reference"
echo ""
sleep 1

# ============================================================================
# FINAL STATUS
# ============================================================================
echo "═══════════════════════════════════════════════════════════════════════"
echo "FINAL STATUS"
echo "═══════════════════════════════════════════════════════════════════════"
echo ""
echo "Checking memory system status:"
python simplemem_status.py | jq '{installed, configured, ready, database_size_mb}'
echo ""

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                       DEMONSTRATION COMPLETE                         ║"
echo "║                                                                      ║"
echo "║  Key Takeaways:                                                      ║"
echo "║  • Claude detects save/recall triggers automatically                 ║"
echo "║  • Tools are called via bash (python script.py args)                 ║"
echo "║  • Memory persists across sessions                                   ║"
echo "║  • Context tags organize information by category                     ║"
echo "║  • All operations return JSON for programmatic use                   ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Show example of querying multiple topics
echo "Example: Query all saved information"
echo "─────────────────────────────────────────────────────────────────────"
echo ""
echo "All preferences:"
python simplemem_recall.py "preferences" --text || echo "(none found)"
echo ""
echo "All decisions:"
python simplemem_recall.py "decisions" --text || echo "(none found)"
echo ""
echo "Database-related:"
python simplemem_recall.py "database" --text || echo "(none found)"
echo ""

# SimpleMem: Persistent Memory for Claude Code

A Claude Code plugin that adds persistent semantic memory across sessions. Save information from conversations and automatically retrieve relevant context when you need it.

Uses vector embeddings and intelligent compression to achieve 30× token reduction compared to full context approaches.

## Installation

### Setup

```bash
# Check if SimpleMem is installed
python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project

# Install SimpleMem
python ~/.claude/plugins/simplemem/tools/simplemem_install.py

# Set your API key
export OPENAI_API_KEY="sk-your-key-here"
```

## Usage

### Save Information
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_save.py "I prefer PostgreSQL for databases" --project
```

### Retrieve Information
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_recall.py "database preferences" --project
```

### Check Status
```bash
python ~/.claude/plugins/simplemem/tools/simplemem_status.py --project
```

## Skills

SimpleMem provides Claude with three skills for autonomous memory management:

- **save-memory** - Automatically saves important information when you ask Claude to remember something
- **recall-memory** - Retrieves relevant past context when answering questions about previous discussions
- **status** - Verifies SimpleMem installation and system health

See `skills/` directory for detailed skill documentation.

## Features

- **Persistent Memory**: Context survives across sessions (days/weeks/months)
- **Semantic Search**: Find relevant information without exact keyword matches
- **Project Isolation**: Separate memory per codebase
- **Local Storage**: All data stored locally, never sent to cloud
- **Smart Compression**: 3-stage pipeline converts conversations into atomic facts

---

## License

MIT License - see LICENSE file for details.

## Attribution

SimpleMem plugin wraps the original SimpleMem research project by Liu et al. (2025).

**Citation:**
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

**Vector Database:** [LanceDB](https://lancedb.com)

**Claude Code:** [claude.com/claude-code](https://code.claude.com)

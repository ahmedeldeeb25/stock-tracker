# .claude Folder

This folder contains AI assistant resources for the Stock Tracker project.

---

## 🚀 Quick Start for AI Assistants

**New session? Start here:**
```bash
cat .claude/CLAUDE.md           # Read the main guide
cat .claude/sessions/LATEST.md  # Read latest session
```

---

## 📁 Folder Contents

### `CLAUDE.md`
Main entry point for AI assistants. Contains workflows, best practices, and folder structure documentation.

### `/sessions/`
Session handover notes documenting changes, decisions, and progress.
- **LATEST.md** - Symlink to most recent session
- **YYYY-MM-DD.md** - Dated session files

### `/context/`
Project context for quick understanding without reading entire codebase.
- **project-overview.md** - High-level project summary
- **tech-stack.md** - Technologies and patterns
- **api-reference.md** - API endpoints documentation
- **component-map.md** - Component locations and purposes

### `/guides/`
How-to guides and best practices.
- **docs-index.md** - Documentation navigation (moved from root)
- **common-patterns.md** - Code patterns to follow

### `settings.local.json`
Claude Code settings file (auto-generated).

---

## 🎯 Purpose

This folder enables:
1. **Session Continuity** - Pick up where the last session left off
2. **Context Preservation** - Understand project without re-exploring
3. **Consistent Patterns** - Follow established conventions
4. **Efficient Collaboration** - Reduce repeated questions

---

## 📝 Maintenance

**After each session:**
1. Create session file: `.claude/sessions/YYYY-MM-DD.md`
2. Update symlink: `ln -sf YYYY-MM-DD.md LATEST.md`
3. Update context files if architecture changed
4. Update guides if new patterns introduced

---

## 👥 For Users

If you're a human user (not an AI assistant):
- This folder is primarily for AI collaboration
- Main documentation is in the root directory
- See `START_HERE.txt` or `README.md` for getting started

---

**Last Updated**: February 7, 2026

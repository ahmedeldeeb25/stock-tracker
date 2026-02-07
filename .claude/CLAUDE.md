# 🤖 Claude AI Assistant Guide

**Stock Tracker Project - AI Collaboration Hub**

This folder contains all resources for AI assistants (Claude, etc.) to effectively work on this project with full context preservation across sessions.

---

## 📍 Quick Start for New Sessions

### Step 1: Read Session History
```bash
# Always start by reading the latest session
cat .claude/sessions/LATEST.md
```

### Step 2: Review Project Context
```bash
# Understand the current project state
cat .claude/context/project-overview.md
```

### Step 3: Check Documentation Index
```bash
# Find relevant documentation quickly
cat .claude/guides/docs-index.md
```

---

## 📁 Folder Structure

```
.claude/
├── CLAUDE.MD                           # This file - main entry point
├── settings.local.json                 # Claude Code settings
├── sessions/                           # Session handover notes
│   ├── LATEST.md                       # → Symlink to most recent session
│   ├── 2026-02-07.md                  # Today's session
│   └── [future sessions...]
├── context/                            # Project context for AI
│   ├── project-overview.md            # High-level project summary
│   ├── tech-stack.md                  # Technologies and patterns used
│   ├── api-reference.md               # API endpoints reference
│   └── component-map.md               # Component locations and purposes
└── guides/                             # How-to guides for AI
    ├── docs-index.md                  # Documentation navigation
    ├── common-patterns.md             # Code patterns to follow
    └── troubleshooting.md             # Common issues and solutions
```

---

## 🎯 Purpose of Each Directory

### `/sessions/` - Session Continuity
**Purpose**: Preserve work history and enable seamless session transitions

**Contents**:
- Date-stamped session notes (YYYY-MM-DD.md)
- What was built, changed, or fixed
- Decisions made and why
- Known issues discovered
- Next steps and TODOs

**When to use**:
- Start of every new session (read LATEST.md)
- End of every session (create new dated file)

---

### `/context/` - Project Understanding
**Purpose**: Quick project comprehension without reading entire codebase

**Contents**:
- Project architecture overview
- Technology stack details
- Database schema
- API endpoint reference
- File structure maps

**When to use**:
- When you need to understand the project structure
- Before making architectural decisions
- When implementing new features

---

### `/guides/` - Best Practices
**Purpose**: Ensure consistent code quality and patterns

**Contents**:
- Documentation index and navigation
- Code patterns and conventions
- Common tasks and how-tos
- Troubleshooting guide

**When to use**:
- Before writing new code
- When stuck on a problem
- When looking for existing documentation

---

## 🚀 Workflow for AI Assistants

### Starting a New Session

1. **Read the latest session**:
   ```bash
   cat .claude/sessions/LATEST.md
   ```

2. **Review project overview** (if unfamiliar):
   ```bash
   cat .claude/context/project-overview.md
   cat .claude/context/tech-stack.md
   ```

3. **Understand the user's request**

4. **Check relevant guides**:
   - Need to add a component? Read `common-patterns.md`
   - Need documentation? Check `docs-index.md`
   - Hit an error? Check `troubleshooting.md`

### During Development

1. **Follow established patterns** from `common-patterns.md`
2. **Reference API docs** from `api-reference.md`
3. **Check component map** for where to add code
4. **Update documentation** as you make changes

### Ending a Session

1. **Create session handover**:
   ```bash
   # Create new dated session file
   .claude/sessions/YYYY-MM-DD.md
   ```

2. **Include in handover**:
   - ✅ What was completed
   - 🔧 What was changed (files, dependencies)
   - 📝 Decisions made
   - 🐛 Known issues
   - 📋 TODOs for next session
   - 💡 Suggestions for future

3. **Update LATEST.md symlink**:
   ```bash
   ln -sf YYYY-MM-DD.md LATEST.md
   ```

4. **Update context files if needed**:
   - New components? Update `component-map.md`
   - New APIs? Update `api-reference.md`
   - New patterns? Update `common-patterns.md`

---

## 📋 Session Handover Template

```markdown
# Session Handover - YYYY-MM-DD

## 🎯 Objectives
- [ ] Objective 1
- [ ] Objective 2

## ✅ Completed
- Feature/fix description with file locations

## 🔧 Changes Made
- File: path/to/file.ext
  - What changed
  - Why it changed

## 📦 Dependencies Added
- package-name@version - Purpose

## 🐛 Known Issues
- Issue description and temporary workaround

## 📝 Important Decisions
- Decision: Rationale

## 💡 Future Enhancements
- Suggestion for next time

## 🧪 Testing
- How to test the changes

## 📊 Session Stats
- Files changed: X
- Lines added: X
- Duration: X hours
```

---

## 🔑 Key Principles

### 1. **Context Preservation**
Every session should be documented so the next session can continue seamlessly without repeating questions or rediscovering information.

### 2. **Consistent Patterns**
Follow established code patterns and conventions. Don't introduce new patterns without documenting them.

### 3. **Documentation Updates**
When you change code, update the relevant documentation. Keep context files in sync with reality.

### 4. **Clear Communication**
Write handovers as if explaining to a colleague who will continue your work. Be specific about file paths, decisions, and reasoning.

### 5. **Incremental Progress**
Document progress even if incomplete. It's better to have partial notes than to start from scratch next time.

---

## 📚 Integration with Main Documentation

The `.claude` folder **complements** (not replaces) the main documentation:

| Main Docs | Claude Docs | Purpose |
|-----------|-------------|---------|
| README.md | context/project-overview.md | README for users, Overview for AI |
| ARCHITECTURE.md | context/tech-stack.md | Detailed for humans, Quick reference for AI |
| QUICKSTART.md | guides/common-patterns.md | User commands vs. Code patterns |
| [New features] | sessions/YYYY-MM-DD.md | What changed, when, and why |

**Rule**: Main docs are user-facing, `.claude` docs are AI-facing.

---

## 🎨 Best Practices for AI Assistants

### DO ✅
- Read session history before starting work
- Follow established patterns from guides
- Document decisions and reasoning
- Update context files when structure changes
- Create clear, detailed handovers
- Test changes before documenting as complete

### DON'T ❌
- Start coding without reading latest session
- Introduce new patterns without documenting
- Skip session handover creation
- Assume previous context without verification
- Make architectural changes without discussion
- Leave TODOs undocumented

---

## 🔍 Quick Reference Commands

```bash
# Find latest session
ls -lt .claude/sessions/ | head -n 2

# Search for specific topic in sessions
grep -r "price target" .claude/sessions/

# List all components
cat .claude/context/component-map.md

# Check API endpoints
cat .claude/context/api-reference.md

# View documentation index
cat .claude/guides/docs-index.md
```

---

## 🤝 Contributing to Claude Context

When you make significant changes:

1. **Update session handover** with details
2. **Update context files** if architecture changed
3. **Update guides** if new patterns introduced
4. **Update component map** if files added/moved
5. **Update API reference** if endpoints changed

Keep these files as single source of truth for AI context.

---

## 📞 Contact & Feedback

This system is designed to improve AI collaboration efficiency. If you notice:
- Missing context that would be helpful
- Outdated information in context files
- Better ways to organize this folder

Create a note in the latest session's "Future Enhancements" section.

---

**Version**: 1.0
**Created**: February 7, 2026
**Last Updated**: February 7, 2026
**Maintained by**: AI sessions with user approval

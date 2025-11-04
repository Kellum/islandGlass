# Checkpoint Archive System - Maintenance Guide

## Purpose

This archive system keeps `checkpoint.md` lean and efficient (~5k tokens) while preserving all historical project context. This reduces context loading time and token costs while maintaining full project history.

## When to Archive

Archive sessions from `checkpoint.md` when ANY of these triggers occur:

1. **File Size**: checkpoint.md exceeds 700 lines
2. **Token Count**: checkpoint.md exceeds 10k tokens
3. **Time**: Sessions older than 2-3 weeks
4. **Session Count**: More than 3 sessions in checkpoint.md
5. **Active Development**: Before starting major new features

## How to Archive

### Step 1: Identify Sessions to Archive

Keep in `checkpoint.md`:
- ✅ Current Status section (always at top)
- ✅ Most recent 2-3 sessions with full details
- ✅ Session Recovery Instructions section
- ✅ Documentation System explanation

Archive to `archive/session-X-description.md`:
- 📦 Older sessions (3+ sessions back)
- 📦 Completed feature work
- 📦 Historical debugging sessions

### Step 2: Create Archive File

**Naming Convention**: `archive/session-X-brief-description.md`

**Examples**:
- `session-1-initial-setup.md`
- `session-2-google-places-integration.md`
- `session-3-claude-enrichment.md`
- `session-4-ui-dashboard.md`
- `session-5-rls-security.md`

**File Structure Template**:
```markdown
# Session X: [Title] - [Date]

## Summary
[2-3 sentences describing main accomplishments]

## Work Completed
- [Detailed bullet points with file paths]
- [Specific features implemented]
- [Tests written/passed]

## Challenges & Solutions
1. **[Challenge Name]**
   - Problem: [Description]
   - Solution: [How it was resolved]
   - Files: [file.py:123-145]
   - Key Learning: [Takeaway]

## Key Files Modified
- `path/to/file.py:123-145` - [What changed and why]
- `path/to/another.py:50-75` - [What changed and why]

## Technical Details
[Code snippets, error traces, API details, debugging notes]

## Configuration Changes
- [Environment variables added/modified]
- [Dependencies added/updated]
- [Database schema changes]

## Lessons Learned
- [Key insights from this session]
- [Best practices discovered]
- [What to avoid in future]

## Next Session Context
[Brief note about what should be done next]
```

### Step 3: Update checkpoint.md

Replace full session details with one-line summary + link:

```markdown
## Archived Sessions

- **Session 1** (Oct 15, 2025): Initial setup, database schema, Streamlit foundation → [Details](archive/session-1-initial-setup.md)
- **Session 2** (Oct 15, 2025): Google Places API integration and scraper → [Details](archive/session-2-google-places.md)
```

### Step 4: Update checkpoint-archive.md

Add entry to the index:

```markdown
## October 2025

### Session 1: Initial Setup - October 15, 2025
[Link](archive/session-1-initial-setup.md)

**Summary**: Set up project foundation with Supabase database, created schema with contractors/outreach/logs tables, built basic Streamlit app with 6 pages, verified database connection with test data.

**Key Accomplishments**:
- ✅ Supabase PostgreSQL database with complete schema
- ✅ Streamlit app structure with multi-page navigation
- ✅ Database connection class with CRUD operations
- ✅ Test data insertion and verification

**Files Created**: `modules/database.py`, `app.py`, `supabase_schema.sql`
```

### Step 5: Verify Archive Integrity

Before committing archive:
- ✅ Confirm archive file is properly formatted
- ✅ Verify all links work in checkpoint.md
- ✅ Check checkpoint-archive.md index is updated
- ✅ Ensure no critical info was lost
- ✅ Confirm checkpoint.md is under 400 lines

## Archive File Naming Conventions

### Format
`session-[number]-[brief-description].md`

### Description Guidelines
- 2-4 words max
- Lowercase with hyphens
- Focus on main feature/topic
- Be specific but concise

### Good Examples
- `session-1-initial-setup.md`
- `session-2-google-places-api.md`
- `session-3-claude-enrichment.md`
- `session-4-ui-overhaul.md`
- `session-5-database-security.md`
- `session-6-dash-migration.md`

### Bad Examples
- ❌ `session-1.md` (not descriptive)
- ❌ `session-2-work.md` (too vague)
- ❌ `oct-15-session.md` (use session numbers)
- ❌ `session-3-Fixed-Multiple-Issues-And-Updated-Code.md` (too long, wrong case)

## Maintenance Schedule

### Weekly (for active projects)
- Check checkpoint.md line count
- Archive if >500 lines

### After Major Milestones
- Archive completed feature work
- Update checkpoint-archive.md with key learnings

### Monthly (for stable projects)
- Review archive structure
- Consolidate checkpoint-archive.md if needed
- Verify all archive links work

## What to Preserve in checkpoint.md

### Always Keep
1. **Current Status** section at top
2. **Most recent 2-3 sessions** with full details
3. **Session Recovery Instructions**
4. **Documentation System** explanation
5. **Quick reference commands** (if applicable)

### Always Archive
1. Sessions older than 3 sessions back
2. Completed feature implementations
3. Historical debugging sessions
4. One-off fixes or patches

### Never Archive
1. Current Status section
2. Active session work
3. Unresolved blockers
4. Next steps for current work

## Token Savings

### Before Archive System
- checkpoint.md: ~25k-30k tokens
- Load time: High
- Context window: Mostly historical

### After Archive System
- checkpoint.md: ~5k tokens (80% reduction)
- archive files: ~2-4k tokens each (loaded only when needed)
- checkpoint-archive.md: ~1k tokens
- Load time: Fast
- Context window: Focused on current work

**Estimated Savings**: 60-70% token reduction per session

## Troubleshooting

### "I can't find historical context"
→ Check `checkpoint-archive.md` index and navigate to specific session archive

### "Archive file is too large"
→ Split into multiple sessions if a single session >300 lines

### "checkpoint.md still over 500 lines"
→ Archive more sessions (keep only most recent 2 sessions)

### "Lost important information"
→ Never delete content, only move to archive. Check `archive/` directory

## Quick Reference Commands

```bash
# Check checkpoint.md size
wc -l checkpoint.md

# List all archive files
ls -lh archive/

# Find specific content in archives
grep -r "search term" archive/

# Count total archived sessions
ls archive/ | wc -l
```

## Archive Statistics

- **Target checkpoint.md**: 250-400 lines (~5k tokens)
- **Target archive file**: 100-200 lines (~2-4k tokens)
- **Recommended sessions in checkpoint**: 2-3 recent sessions
- **Archive when**: >700 lines or >3 sessions old

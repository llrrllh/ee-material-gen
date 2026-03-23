---
name: sheet-music-organizer
description: Validate, standardize, and scan Classical/Cello sheet music folders for naming inconsistencies and missing parts. Use when asked to organize sheet music, tidy up music folders, check for missing cello parts, or enforce standard sheet music naming conventions (e.g. converting roman numerals to arabic, Score to Full Score, Violoncello to Cello).
---

# Sheet Music Organizer

This skill provides utilities to maintain a highly structured, standard naming convention for sheet music collections (especially cello ensembles).

## Workflows

### 1. Catalog Auditing (Bilingual Consistency)

When asked to organize the folder to be more systematic ("条理化"), run the auditor. It ensures:
- Composer folders are bilingual: `English Name (中文译名)`
- Piece filenames are bilingual: `English Title(中文标题)_Op.XX_Cello 1.pdf`

```bash
python3 scripts/audit_naming.py "/path/to/sheet/music"
```

### 2. Standardizing Part Names

When asked to standardize or fix naming in a sheet music folder, run the normalization script.

```bash
# Preview changes first
python3 scripts/normalize_parts.py "/path/to/sheet/music" --dry-run

# Execute changes (will automatically handle case-conflicts by trashing duplicates)
python3 scripts/normalize_parts.py "/path/to/sheet/music"
```

The script automatically fixes common errors:
- `Score` or `fullscore` → `Full Score`
- `complete` → `Complete`
- `Violoncello 1` or `Cello I` → `Cello 1`
- `cello1` or `大提琴1` → `Cello 1`

For the exact naming schema enforced by this tool, read `references/naming-rules.md`.

### 2. Scanning for Missing Parts

When asked to find out what's missing from an ensemble collection (e.g. "what parts are missing?", "check incomplete pieces"), run the scanner script.

```bash
python3 scripts/scan_missing.py "/path/to/sheet/music"
```

The scanner groups files by composer and piece, and outputs two categories:
- **Category B (Critical)**: Pieces that have some parts (like Cello 2, Cello 4) but are missing others (Cello 1, Cello 3, or Full Score)
- **Category A (Minor)**: Pieces that have all their playing parts but lack a conductor's `Full Score`

### 3. Finding Replacements

When missing parts are identified, search for them on [IMSLP (International Music Score Library Project)](https://imslp.org). 

If IMSLP links block direct `curl` downloads via anti-hotlinking disclaimers:
1. Provide the user with a markdown list of direct IMSLP page links to click and download manually.
2. Clearly indicate the expected final filename (e.g. `Piece Name_Op. X_Cello 1.pdf`) so the user can save it correctly.

> Note: Popular/Anime/Chinese folk songs (e.g. Joe Hisaishi, pop arrangements) are usually under copyright or not part of the classical canon, and will *not* be found on IMSLP.

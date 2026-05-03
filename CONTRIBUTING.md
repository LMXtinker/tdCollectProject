# Contributing to CollectTDProject

## Development Setup

The development source is `CollectTDProject_dev.toe`. Open this in TouchDesigner to work on the component. When ready to release, export the inner COMP as a `.tox` via right-click → **Save Component**.

### Internal Architecture

The component is a single `containerCOMP` with a Python extension class (`Helpers` textDAT, promoted via `extension1`). Two CHOP Execute scripts drive the main logic:

| Script | Role |
|--------|------|
| `scanning_chopExec` | Recursive scan, writes results to `Files_Table`, reports total file size |
| `chopexec1` | Reads `Files_Table`, runs file transfer, rewrites parameters |

The extension class (`CollectExt`) provides shared helpers: `Write_log()`, `Get_exclude_list()`, `Get_scan_root()`, `Record_undo_par()`, `Record_undo_file()`, `Undo_last_consolidate()`, etc.

Access from any script inside the component via `me.parent()` (which resolves to the root COMP with the promoted extension).

### Code Rules

1. **No `print()` for user feedback.** Use `tool.Write_log(message)` — `tool` is `me.parent()`.
2. **No `os.rename()` for cross-drive file moves.** Use `shutil.move()` or `os.replace()` as already implemented.
3. **Wrap all parameter evaluation in `try/except`.** TD parameters frequently contain broken expressions.
4. **Log messages must be concise.** Prefix with a standard Unicode icon: `✅`, `🔍`, `⚙`, `ⓧ`. Avoid complex emoji.
5. **Do not break the `me.parent().op('Log')` reference.** The `Write_log()` function depends on the relative path to the `Log` DAT.

---

## Versioning Strategy

`.tox` files are binary — Git diffs are not meaningful. Use this workflow:

### Tagging Releases

Use [Semantic Versioning](https://semver.org/): `vMAJOR.MINOR.PATCH`

- **PATCH** (`v1.0.1`): Bug fixes, no behavior change.
- **MINOR** (`v1.1.0`): New features, backwards-compatible.
- **MAJOR** (`v2.0.0`): Breaking changes (parameter renames, removed functionality).

### Release Workflow

1. Make changes in the `.toe` dev file, test thoroughly.
2. Update `par.Version` on the component's About page to the new version string.
3. Update `par.Toxsavebuild` to the current TD build (`app.build`).
4. Export the component as `CollectTDProject.tox` (right-click the COMP → Save Component).
5. Copy the `.tox` to `releases/CollectTDProject.tox` (overwrites latest).
6. Commit: `git add releases/CollectTDProject.tox && git commit -m "release: v1.2.0 - description"`
7. Tag: `git tag v1.2.0`
8. Push: `git push && git push --tags`
9. Create a GitHub Release from the tag, attach the `.tox` as a release asset.

### File Naming Convention

| File | Purpose |
|------|---------|
| `releases/CollectTDProject.tox` | Latest stable — always overwritten in-place |
| `src/CollectTDProject_dev.toe` | Active development source |
| `examples/example_project.toe` | Minimal working example for new users |

Do not commit version numbers into file names (e.g., `CollectTDProject_v1.2.tox`). Use Git tags for version tracking instead. This keeps the download URL stable: users always grab `releases/CollectTDProject.tox` regardless of version.

---

## Suggested Repository Structure

```
CollectTDProject/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── .gitignore
├── releases/
│   └── CollectTDProject.tox       # Latest stable .tox (committed binary)
├── src/
│   └── CollectTDProject_dev.toe   # Dev source — open this to make changes
├── examples/
│   └── example_project.toe        # Minimal project with the .tox pre-loaded
└── docs/
    ├── handoff.md                  # Architecture + dev notes
    └── screenshots/
        └── ui_overview.png
```

### `.gitignore` for TouchDesigner projects

```gitignore
# TD auto-saves
*.toe.bak
Backup/

# OS noise
.DS_Store
Thumbs.db

# Large media — add to repo only if intentional
*.wav
*.mp3
*.mp4
*.mov
*.exr
*.hdr
*.tif
*.tiff
```

---

## License & Attribution

This project is licensed under **GPL-3.0**. It is a derivative of [TD-File-Collector](https://github.com/mourendxu/TD-File-Collector) by mourendxu (GPL-3.0). All contributions must be compatible with GPL-3.0.

The two scripts derived from the original project (`scanning_chopExec`, `chopexec1`) carry the following header — do not remove it:

```python
# Derived from TD-File-Collector by mourendxu
# https://github.com/mourendxu/TD-File-Collector — GPL-3.0
```

---

## Reporting Bugs

Open a GitHub Issue. Include:

- TouchDesigner version (`Help → About`)
- Operating system
- A description of the project structure (rough network layout, file types referenced)
- The full log output from the component after the failure

# CollectTDProject — Claude Code Context

> TOX on disk: v1.3.0 · Latest release: v1.3.0 (broken-path detection, replayable relocation log, preset auto-increment + smart defaults, redesigned panel UI)

## Project

TouchDesigner utility. Scans project network for external file dependencies, copies/moves them into local folder structure, rewrites OP parameters to relative paths.

Repo: https://github.com/LMXtinker/CollectTDProject
Branch: `master` (direct commits)
Dev source: `CollectTDProject_dev.toe` (open in TD to make changes)
Distributable: `CollectTDProject.tox` (commit after saving from TD)

---

## Briefing Shortcut

When the user says **"brief yourself with the project"** :
- `HANDOFF.md`
- `CONTRIBUTING.md`
- `README.md`


---

## Session Start Checklist

Do this first:

1. Run `ToolSearch` for `mcp__twozero_td` — confirm tools resolve.
2. Call `mcp__twozero_td__td_list_instances` — confirm TD is running and active project is `CollectTDProject_dev*.toe`.
3. If tools fail, open TouchDesigner and start MCP server from TD palette (port **40404**).
4. Read `HANDOFF.md` for the most recent session work and pending tasks.

### TD MCP Connection — How It Works

- Config: `.mcp.json` in project root + `enabledMcpjsonServers: ["twozero_td"]` in `~/.claude/settings.json`
- Tools load **at session start only**. If TD MCP server wasn't running when the session opened, tools won't appear — no matter what you do after.
- `ToolSearch("mcp__twozero_td")` returning empty = session started before TD was ready.
- **Fix**: ensure TD is running and MCP server is active on port 40404, then **start a fresh session**.
- Do NOT edit `claude_desktop_config.json` — the `.mcp.json` mechanism is correct and sufficient.
- Verify server is live: `curl -X POST http://localhost:40404/mcp` should return `{"error":"method not allowed","allow":"POST"}`.
- If tools load but connection drops mid-session: tools will still appear in deferred list but calls will fail. Ask user to restart TD MCP server, then continue — tools stay available for the session.

---

## Pending Tasks

### 1. (Optional) `tests/README.md`

Add a brief doc explaining how to use `tests/demo_broken_paths.tox` for manual testing. The demo's broken paths now correctly appear in scanner output (v1.3.0 broken-path detection); document the expected `⚠ ... missing on disk` log entries.

### 2. (Optional) End-to-end CONSOLIDATE test with real assets

`tests/create_demo.py` only creates broken-path nodes. To exercise the transfer + relocation log paths, either ship a small `tests/assets/` folder (jpg, mp4, wav, ttf, fbx, json, glsl, tox samples) or extend `create_demo.py` to write tiny placeholder files before saving the `.tox`. Verify that running the generated `<project>.relocation_*.py` correctly rolls back a Move-mode consolidation.

### 3. (Optional, separate) Investigate textport errors

- `td.tdAttributeError: 'td.OPShortcut' object has no attribute 'FNS_BORDERLESS' Context:/ui/dialogs/mainmenu/menu/saveStateScriptOp_callbacks` — TD system, not this project.
- `ValueError: invalid literal for int() with base 10: '4.5'` — source not pinpointed. Possibly a CHOP→string conversion feeding maxdepth or similar.

Neither blocks new releases.

---

## Architecture

### Key Scripts (read via MCP)

| Op path | Role |
|---------|------|
| `op('/project1/CollectTDProject/chopexec1')` | Consolidator — reads Files_Table, skips missing-source rows, transfers files, rewrites pars, writes relocation log |
| `op('/project1/CollectTDProject/scanning_chopExec')` | Scanner — evaluates all string pars, classifies refs (existing local relative / broken / external / absolute), writes to Files_Table including `Exists` column |
| `op('/project1/CollectTDProject/ui/panel_callbacks')` | Panel dispatch + tooltip logic |
| `op('/project1/CollectTDProject/Helpers')` | Extension class source (`ConsolidateExt`) |

### Extension Class (`ConsolidateExt`)

Access from any script inside component via `me.parent()` (parentshortcut: `tool`). Promoted, so `tool.<Method>()` works directly.

| Method | Purpose |
|--------|---------|
| `Write_log(msg)` | Append a line to Log DAT |
| `Clear_log()` | Clear Log DAT |
| `Log_header(action, *segments)` | Write timestamped section header |
| `Log_summary(items)` | Write aligned summary block |
| `Get_scan_root()` | Resolve scan root COMP |
| `Get_exclude_list()` | Parse excluded file extensions |
| `Get_excluded_comp_paths()` | Parse excluded COMP paths |
| `Get_max_depth()` | Return max recursion depth (0 = unlimited) |
| `Should_ignore_palette()` | Return ignore-palette toggle value |
| `Is_system_path(path)` | True if path under /ui or /sys |
| `Is_palette_comp(node)` | True if node is palette/packaged COMP |
| `Refresh_status(action)` | Update Status_Data DAT |
| `Reset_undo_log()` | Clear and re-seed Undo_Log |
| `Record_undo_par(op_path, par_name, old_val)` | Log parameter change for undo |
| `Record_undo_file(src, dst, mode)` | Log file transfer for undo |
| `Undo_last_consolidate()` | Reverse last consolidation |
| `Status_line()` | Return formatted status bar string |
| `Reset_all_params()` | Reset all operational pars to defaults (preserves Scanroot, preset pars) |
| `Reset_par(name)` | Reset a single named par to its default |
| `Save_preset()` | Write current pars to `{Presetpath}/{Presetname}.json`. Defaults: folder→`~/Documents/Derivative/CollectTDProject`, name→`preset_<project_stem>`. Auto-increments suffix on filename collision. |
| `Load_preset()` | Read JSON from `{Presetpath}/{Presetname}.json` and apply pars |
| `Backup_original_toe()` | Copy on-disk `.toe` to `<stem>.original.toe` (idempotent — only writes once) |
| `Write_relocation_log(entries, mode)` | Write `<project>.relocation_<TS>.py` next to `.toe`. Self-contained replay file: `python <file>.py` rolls back the consolidation (move back / delete copy / flag overwrite as unrecoverable) |

`RESETTABLE_PARS` (module-level constant in Helpers): the canonical list of pars touched by Reset/preset save/load. Edit this when adding a new operational par.

### Extension Categories Map (`chopexec1` → `Dirs`)

| Folder | Extensions |
|--------|-----------|
| `Image/` | jpg jpeg png gif bmp tif tiff exr hdr tga dds svg pic |
| `Movie/` | mp4 mov avi wmv mpeg mpg mkv |
| `Audio/` | mp3 wav aiff aif ogg flac |
| `Font/` | ttc ttf otf |
| `Geo/` | fbx obj abc dae usd usda usdc usdz ply stl dxf |
| `Data/` | txt json xml csv dat py yaml yml toml glsl frag vert hlsl |
| `Component/` | tox |

Add new extension to `Dirs` (chopexec1) AND `_PRESETS` (panel_callbacks).

### Panel Dispatch System

Single `panelexecuteDAT` at `ui/panel_callbacks`. **Critical**: TD does NOT auto-recurse into a parent COMP — every interactive panel must be enumerated (or matched by wildcard expressions).

Required parameter state:

| Par | Mode | Value |
|-----|------|-------|
| `par.panels` | EXPRESSION | wildcard expression listing all interactive panels |
| `par.panelvalue` | CONSTANT | `'select inside'` (space-separated) |
| `par.offtoon`, `par.ontooff`, `par.valuechange`, `par.active` | CONSTANT | `True` |

Mode flipping `par.panels` to CONSTANT silently kills all dispatch. Always edit via `cb.par.panels.expr = '...'` and verify `cb.par.panels.mode == ParMode.EXPRESSION`.

The expression covers:
- `ui/actions/*` — main action buttons (FIND, CONSOLIDATE, UNDO)
- `ui/param_actions/*` — preset+reset row (SAVE, LOAD, RESET — v1.3.0+ split out of actions)
- `ui/log_view/btn_clear`, `ui/footer/btn_instagram` — single explicit panels
- `ui/config/*/tgl_*`, `ui/config/*/seg_*/*`, `ui/config/*/preset_*` — toggles, segmented, presets
- `ui/config/*` — direct children of config (rows, headers, dividers) for tooltips

Dispatch is name-based via `panelValue.owner.name`:

- `_TOGGLES` — binary toggles (Modifyparams, Ignorepalettecomps, Backupbeforeconsolidate)
- `_FIELD_RESETS` — per-field reset buttons (btn_reset_types, btn_reset_comps)
- `_INDEXED` — segmented buttons with numeric suffix (seg_mode_0/1, seg_conflict_0/1/2)
- `_PRESETS` — exclusion preset toggles (preset_img, preset_vid, etc.)
- Direct name match — action buttons (btn_find, btn_consolidate, btn_undo, btn_clear, btn_instagram, btn_save_preset, btn_load_preset, btn_reset_global)

`onOffToOn` / `onOnToOff` both guard on `panelValue.name == 'select'` to prevent `inside` events from triggering button dispatch.

### Tooltip System

- `_TOOLTIP` dict in `panel_callbacks` maps panel name → help text
- `onValueChange` checks `panelValue.name == 'inside'` (NOT `rolloveron`/`rolloveroff` — those don't exist on containerCOMPs)
- Active text written to `ui/tooltip` textDAT; `ui/status.par.text` expression reads it (falls back to `parent.tool.Status_line()` when empty)

To add a new tooltip: add entry to `_TOOLTIP` dict; ensure the panel is matched by the `par.panels` expression.

### Bind-Linked Text Inputs

`tin_*` textCOMPs use `par.editmode = 'editable'` and bind `par.text` to the corresponding root custom par:

| Text input | Bound to |
|------------|----------|
| `tin_scanroot` | `parent.tool.par.Scanroot` |
| `tin_maxdepth` | `parent.tool.par.Maxdepth` |
| `tin_xtypes` | `parent.tool.par.Excludefiletypes` |
| `tin_xcomps` | `parent.tool.par.Excludecomps` |

Bind is two-way. Read via `par.text.eval()`, NOT `par.text.val` (the latter is the literal stored text).

### Internal DATs

| DAT | Role |
|-----|------|
| `Files_Table` | Found files: Directory, Filename, Extension, OP Path, Filesize, ParamName, Exists ('1' / '0') |
| `Log` (fifoDAT) | Real-time scrolling log |
| `Undo_Log` (tableDAT) | Reversible actions for single-step undo |
| `Status_Data` (tableDAT) | Summary row for status bar |
| `Helpers` (textDAT) | Extension class source |
| `ui/tooltip` (textDAT) | Active hover tooltip text |

### Custom Parameter Pages

| Page | Key Parameters |
|------|---------------|
| Consolidate | Scanroot, Maxdepth, Findfiles, Consolidatefiles, Undo, Movefiles, Modifyparams, Conflictstrategy, Backupbeforeconsolidate, Clearlog |
| Exclusions | Ignorepalettecomps, Excludecomps, Excludefiletypes |
| Presets | Presetpath, Presetname (no panel UI — set via custom pars on COMP). Both blank → defaults to `~/Documents/Derivative/CollectTDProject/preset_<project_stem>.json`. |
| Style | Color tokens (Bgr/g/b, Btnr/g/b, etc.) |
| About | Version (readOnly), Toxsavebuild (readOnly), Help |

---

## Code Rules

1. **No `print()` for user feedback.** Use `tool.Write_log(message)`.
2. **No `os.rename()` for cross-drive moves.** Use `shutil.move()` or `os.replace()`.
3. **Wrap parameter evaluation in `try/except`.** TD pars often broken.
4. **Log message prefixes:** `✓` success, `✗` error/skip, `·` neutral, `⚠` warning, `+` created, `→` transferred, `🛡` safety backup, `📋` relocation log.
5. **Extensions added to `Dirs` AND `_PRESETS`** for full support.
6. **Do not break `me.parent().op('Log')` reference.** `Write_log()` depends on it.
7. **Never set `par.panels` via `.val =`** on `panel_callbacks` — switches mode to CONSTANT and kills dispatch silently. Use `cb.par.panels.expr = '...'`.
8. **`Files_Table` columns are read by header name** in `chopexec1` (`_col_index()` helper). Adding a new column does not break the consolidator.
9. **New operational pars must be added to `RESETTABLE_PARS`** in `Helpers` so reset + preset save/load cover them.

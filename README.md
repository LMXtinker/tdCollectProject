# CollectTDProject

A TouchDesigner utility component that scans your project for external file dependencies, copies or moves them into a local folder structure, and rewrites operator parameters to relative paths — making your project fully portable.

---

## The Problem

TD projects reference files by absolute path (`C:/Users/studio/assets/image.png`). Move the project to another machine or share it, and those references break. Manually hunting and relinking files is tedious and error-prone.

CollectTDProject automates the whole process.

---

## Features

- Recursive scan of the entire project network, or a defined subtree
- Detects file references across all operator types by evaluating string parameters
- Organizes collected files into standard subfolders: `Image/`, `Movie/`, `Audio/`, `Geo/`, `Data/`, `Font/`, `Component/`
- **Copy or Move** — non-destructive copy mode by default
- **Conflict resolution** — Skip, Overwrite, or Auto-rename when a file already exists at the destination
- **Rewrites OP parameters** to relative paths after transfer (optional, on by default)
- **File size calculator** — shows total dependency size before you commit to anything
- **Undo** — reverses the last consolidation, restoring original parameter values (and returning moved files in Move mode)
- **Exclusion presets** — one-click toggles for Images, Video, Audio, 3D/Geo, Data, and TOX file groups
- **Palette/system exclusion** — skips components sourced from the TD palette and internal system paths
- Custom **scan scope**: set a root COMP and max recursion depth
- **Exclusion lists**: skip specific COMPs or file extensions
- Live **status bar** always showing current conflict mode, file count, and last action
- Scrollable real-time **log viewer** with ample space for long path lists
- Self-contained: single `.tox`, no external Python packages or dependencies

---

## Requirements

- TouchDesigner 2025.32460 or later
- Python 3.11+ (bundled with TD 2025)
- Windows or macOS

---

## Installation

1. Download `CollectTDProject.tox` from the [Releases](../../releases/latest) page.
2. In TouchDesigner, drag the `.tox` into any network, or use **OP Create Dialog → From File**.
3. The component is ready immediately — no additional setup.

**Recommended placement:** Drop it at `/project1` so it can reach the full network.

---

## Usage

### Quick Start

1. Open the component viewer (`V` on the node, or click the viewer icon)
2. Click **FIND** — scans the project and lists all found file references and total size in the log
3. Review the log output, adjust exclusions if needed, re-scan
4. Click **CONSOLIDATE** — transfers files and rewrites parameters

### Panel UI

```
┌─────────────┬─────────────────────┬──────────┐
│    FIND     │     CONSOLIDATE     │   UNDO   │
├─────────────┴─────────────────────┴──────────┤
│ Scan Root                        Depth  0    │
├──────────────────────────────────────────────┤
│ Collection mode   [ Copy ]  [ Move ]         │
│ File conflict   [ Skip ] [Overwrite] [Rename]│
├──────────────────────────────────────────────┤
│ EXCLUSIONS                                   │
│ [Images][Video][Audio][3D/Geo][Data][ TOX ]  │
│ Types   .tox, .py                            │
│ COMPs                    Excl. palette  [ON] │
├──────────────────────────────────────────────┤
│ 3 files · 36.4 MB · conflict: Skip · SCAN…  │
├──────────────────────────────────────────────┤
│  ✅ [SCAN 14:23]                             │
│  🔍 /project1/moviefilein1 → Movie/clip.mp4  │
│  🔍 /project1/null1/moviefilein1 → Movie/…  │
│  🔍 /project1/tex1 → Image/logo.png         │
│                                              │
│                                      [CLEAR] │
└──────────────────────────────────────────────┘
```

#### Exclusion Presets

Click any preset to instantly add or remove that file group from the exclusion list:

| Preset | Extensions |
|--------|-----------|
| Images | jpg jpeg png gif bmp tif tiff exr hdr tga psd dds svg |
| Video | mp4 mov avi mkv wmv flv webm m4v mpg mpeg mxf |
| Audio | mp3 wav aiff aif ogg flac aac m4a wma |
| 3D/Geo | fbx obj abc usd usda usdc glb gltf ply stl dae 3ds |
| Data | json xml csv txt yaml toml py glsl frag vert |
| TOX | tox |

Presets are additive — toggling one preset does not affect extensions added manually or by other presets.

---

## Parameters

### Consolidate Page

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Scan Root | String | *(blank)* | COMP path to start scan from. Blank = project root. |
| Max Depth | Integer | 0 | Max recursion depth. `0` = unlimited. |
| Find Files | Pulse | — | Run the file scanner. Reports file count and total size. |
| Consolidate Files | Pulse | — | Run consolidation. |
| Undo | Pulse | — | Undo the last consolidation. |
| Move Files | Toggle | Off | Move files instead of copying. |
| Modify Params | Toggle | On | Rewrite originating OP parameters to relative paths after transfer. |
| Conflict Strategy | Menu | Skip | What to do when a file already exists at the destination. Options: Skip, Overwrite, Rename. |
| Clear Log | Pulse | — | Clear the log viewer. |

### Exclusions Page

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| Ignore Palette COMPs | Toggle | On | Skip components sourced from the TD palette or internal library. |
| Exclude COMPs | String | *(blank)* | Comma-separated COMP paths to exclude (e.g., `/project1/bg_assets, /project1/refs`). |
| Exclude File Types | String | *(blank)* | Comma-separated extensions to skip (e.g., `tox, py, glsl`). |

---

## Internal DATs

These DATs are accessible inside the component if you need to read results programmatically:

| DAT | Contents |
|-----|----------|
| `Files_Table` | All found file references: OP path, parameter name, source path, category, file size |
| `Log` | Full log output from last run |
| `Status_Data` | Summary row: file count, total MB, last action, timestamp, undo state |

---

## Output Folder Structure

After consolidation, files are placed next to your `.toe` file:

```
MyProject/
├── MyProject.toe
├── Image/
├── Movie/
├── Audio/
├── Geo/
├── Data/
├── Font/
└── Component/
```

---

## Undo

Undo reverses **the last consolidation only**:

- **Copy mode**: Restores original parameter values. Files at destination remain (they were copies).
- **Move mode**: Restores original parameter values and moves files back to their original locations.

Undo state is cleared when a new **FIND** scan is run.

---

## Known Limitations

- **Sequence file patterns** (e.g., `frame####.exr`) are not yet detected — only single file path references are picked up.
- File references built dynamically via Python expressions that don't resolve to a plain string at scan time will be missed.
- **Multi-step undo is not supported.** Undo covers the immediately preceding consolidation only.
- Parameters referencing files via `tdu.expandPath()` or similar TD path helpers may not evaluate correctly during scan.

---

## Contributing

Bug reports and pull requests are welcome.

Before opening a PR:

1. Test against a real project with a mix of file types (image, movie, audio, geometry).
2. Verify that Undo correctly restores all parameters in both Copy and Move mode.
3. Confirm palette COMPs (Stoner, etc.) are excluded when the toggle is enabled.
4. Do not add `print()` calls for user feedback — use the `Write_log()` extension method on the component.
5. Preserve all `try/except` blocks around parameter evaluation. TD parameters frequently contain unevaluable expressions.

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup details.

---

## Acknowledgments

Built on top of [TD-File-Collector](https://github.com/mourendxu/TD-File-Collector) by [mourendxu](https://github.com/mourendxu), licensed under GPL-3.0. The core file-scanning and parameter-rewriting approach originates from that project.

---

## License

GPL-3.0 — see [LICENSE](LICENSE).

# Contributing

Thanks for considering a contribution to tdCollectProject. This is a small beta-stage utility — issues and pull requests are welcome.

## Reporting Bugs

Open a [GitHub Issue](../../issues/new?template=bug_report.md). Please include:

- TouchDesigner version (Help → About)
- OS (Windows / macOS)
- Steps to reproduce
- Full log output from the panel after the failure (right-click → Copy on the `Log` DAT inside the COMP — the **COPY PATHS** button copies only the found absolute file paths, not the log)

## Development

The component is authored live inside a TouchDesigner project. There is no build step.

1. Clone the repo.
2. Open a fresh `.toe` and drag in `tdCollectProject.tox` to verify the released component, or open the dev `.toe` if you have one locally (dev `.toe` files are gitignored).
3. Make changes to the COMP — DAT scripts, parameters, UI panels.
4. When ready: right-click the COMP → **Save Component** → overwrite `tdCollectProject.tox`.
5. Commit the updated `.tox` together with any markdown/CHANGELOG changes.

The Python extension class lives in the `Helpers` textDAT (promoted as `ConsolidateExt`, parentshortcut `tool`).

## Code Conventions

- Use `tool.Write_log(message)` for user-facing output, not `print()`.
- Wrap parameter evaluation in `try/except` — TD pars often hold unevaluable expressions.
- Standard log prefixes: `✓` success, `✗` error/skip, `·` neutral, `⚠` warning, `+` ok-on-disk, `→` transfer, `🛡` backup, `📋` clipboard.
- File transfer code path: `shutil.move` / `os.replace` only (no `os.rename` — fails cross-drive on Windows).
- Adding a new operational parameter? Also add it to `RESETTABLE_PARS` in `Helpers` so reset + preset save/load cover it.
- Adding a new file extension? Add to both `Dirs` (chopexec1) and `_PRESETS` (panel_callbacks).
- Touching `ui/panel_callbacks.par.panels`? Edit `cb.par.panels.expr` only — flipping the par to CONSTANT silently kills all UI dispatch.

## License & Attribution

GPL-3.0. Derivative of [TD-File-Collector](https://github.com/mourendxu/TD-File-Collector) by mourendxu (GPL-3.0). Contributions must be GPL-3.0 compatible.

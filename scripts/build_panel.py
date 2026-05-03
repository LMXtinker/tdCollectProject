"""
build_panel.py
==============

Builds the `ui/config` block of CollectTDProject's panel UI: an idiomatic-TD
sub-container that exposes the custom parameters not already covered by the
header buttons (FIND / CONSOLIDATE / UNDO).

Rows added (top to bottom, between `actions` and `status`):
    Scan Root        textCOMP, editable, 2-way bound to par.Scanroot
    Max Depth        textCOMP, editable+integer, 2-way bound to par.Maxdepth
    Mode             segmented Copy/Move (writes par.Movefiles)
    Conflict         segmented Skip/Overwrite/Rename (writes par.Conflictstrategy)
    Rewrite Params   pill toggle (par.Modifyparams)
    Ignore Palette   pill toggle (par.Ignorepalettecomps)
    Exclude Types    textCOMP, editable, par.Excludefiletypes
    Exclude COMPs    textCOMP, editable+multiline, par.Excludecomps

The status bar (`ui/status`) reads `parent.tool.Status_line()` — Status_line
already shows the current conflict mode (see Helpers DAT, near line 192).

USAGE — paste into a textDAT named `build_panel` inside the COMP, then run:
    op('/project1/CollectTDProject/build_panel').run()

Idempotent: destroys `ui/config` and rewrites `ui/panel_callbacks` first.

NOTES on TD idioms (calibrated against td_get_hints('panel_layout')):
    * No fieldCOMP / buttonCOMP / sliderCOMP — TD's docs flag those as legacy.
      Everything is built from containerCOMP + textCOMP + panelexecuteDAT.
    * Expressions reference the root COMP via parent.tool.par.X (parentshortcut
      already set to 'tool'). Survives wrap/copy/rename.
    * Text inputs use ParMode.BIND on par.text → 2-way binding to the custom
      parameter. No callbacks needed for them.
    * Toggles + segmented buttons are wired through the existing
      `ui/panel_callbacks` panelexecuteDAT (re-emitted by this script). Their
      panel names are dispatched by prefix in onOffToOn.
"""

ROW_H        = 28
LBL_W        = 124
TGL_W        = 56
SEG_BTN_W    = 84
SPACING      = 4

CONFLICT_LABELS = ['Skip', 'Overwrite', 'Rename']
MODE_LABELS     = ['Copy', 'Move']


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _expr(par, expr_str):
    par.expr = expr_str
    par.mode = ParMode.EXPRESSION


def _bind(par, expr_str):
    par.bindExpr = expr_str
    par.mode = ParMode.BIND


def _ink(t, dim=False):
    src = ('Inkdimr', 'Inkdimg', 'Inkdimb') if dim else ('Inkr', 'Inkg', 'Inkb')
    _expr(t.par.fontcolorr, f'parent.tool.par.{src[0]}')
    _expr(t.par.fontcolorg, f'parent.tool.par.{src[1]}')
    _expr(t.par.fontcolorb, f'parent.tool.par.{src[2]}')


def _make_label(p, name, text, w=LBL_W):
    t = p.create(textCOMP, name)
    t.par.alignorder = 0
    t.par.hmode, t.par.w, t.par.vmode = 'fixed', w, 'fill'
    t.par.text = text
    t.par.fontsize, t.par.fontsizeunits = 11, 'panelunits'
    t.par.scaletofit = 'never'
    t.par.alignx, t.par.aligny, t.par.alignymode = 'left', 'center', 'bbox'
    t.par.textpaddingl = t.par.textpaddingr = 0
    t.par.bgalpha = 0
    _ink(t, dim=True)
    return t


def _make_row(p, name, alignorder, h=ROW_H):
    c = p.create(containerCOMP, name)
    c.par.alignorder = alignorder
    c.par.hmode, c.par.vmode, c.par.h = 'fill', 'fixed', h
    c.par.align, c.par.spacing = 'horizlr', 8
    c.par.bgalpha = c.par.borderaalpha = 0
    return c


def _make_text_input(p, name, par_path, multiline=False, type_='string', w=None):
    t = p.create(textCOMP, name)
    t.par.alignorder = 1
    if w:
        t.par.hmode, t.par.w = 'fixed', w
    else:
        t.par.hmode = 'fill'
    t.par.vmode = 'fill'
    t.par.editmode = 'editable'
    t.par.type = 'multiline' if multiline else type_
    t.par.fontsize, t.par.fontsizeunits = 11, 'panelunits'
    t.par.scaletofit = 'never'
    t.par.alignx = 'left'
    t.par.aligny = 'top' if multiline else 'center'
    t.par.alignymode = 'metrics' if multiline else 'bbox'
    t.par.textpaddingl = t.par.textpaddingr = 6
    t.par.textpaddingt = t.par.textpaddingb = (4 if multiline else 0)
    t.par.bgalpha = 1
    _expr(t.par.bgcolorr, 'parent.tool.par.Bgr')
    _expr(t.par.bgcolorg, 'parent.tool.par.Bgg')
    _expr(t.par.bgcolorb, 'parent.tool.par.Bgb')
    _ink(t)
    t.par.borderar = t.par.borderag = t.par.borderab = 1
    _expr(t.par.borderaalpha, '0.25 if me.panel.lselect else 0.08')
    for s in ('leftborder', 'rightborder', 'topborder', 'bottomborder'):
        setattr(t.par, s, 'bordera')
    _bind(t.par.text, par_path)
    t.par.cursor = 'iBeam'
    return t


def _make_toggle(p, name, par_path, label_on='ON', label_off='OFF'):
    btn = p.create(containerCOMP, name)
    btn.par.alignorder = 1
    btn.par.hmode, btn.par.w, btn.par.vmode = 'fixed', TGL_W, 'fill'
    btn.par.bgalpha = 1
    on = f'(1.0 if {par_path} else 0.0)'
    for ch, accent, base in (
        ('bgcolorr', 'Btnaccr', 'Btnr'),
        ('bgcolorg', 'Btnaccg', 'Btng'),
        ('bgcolorb', 'Btnaccb', 'Btnb'),
    ):
        _expr(getattr(btn.par, ch),
              f'({on} * parent.tool.par.{accent} + (1-{on}) * parent.tool.par.{base}) '
              f'* (1.2 if me.panel.inside else 1.0)')
    btn.par.borderaalpha = 0
    btn.par.cursor = 'pointer'

    lbl = btn.create(textCOMP, 'lbl')
    lbl.par.hmode = lbl.par.vmode = 'fill'
    lbl.par.bgalpha = 0
    lbl.par.fontsize, lbl.par.fontsizeunits = 11, 'panelunits'
    lbl.par.scaletofit = 'never'
    lbl.par.alignx, lbl.par.alignxmode = 'center', 'metrics'
    lbl.par.aligny, lbl.par.alignymode = 'center', 'bbox'
    lbl.par.bold = True
    _ink(lbl)
    _expr(lbl.par.text, f"'{label_on}' if {par_path} else '{label_off}'")
    return btn


def _make_segmented(p, name, par_path, labels, par_kind='int', w=SEG_BTN_W):
    """par_kind='int' writes raw int (0/1); 'menu' compares + writes menuIndex."""
    seg = p.create(containerCOMP, name)
    seg.par.alignorder = 1
    seg.par.hmode = 'fixed'
    seg.par.w = w * len(labels) + (len(labels) - 1) * 2
    seg.par.vmode = 'fill'
    seg.par.align, seg.par.spacing = 'horizlr', 2
    seg.par.bgalpha = seg.par.borderaalpha = 0

    state = par_path if par_kind == 'int' else f'{par_path}.menuIndex'
    for i, lab in enumerate(labels):
        b = seg.create(containerCOMP, f'{name}_{i}')
        b.par.alignorder = i
        b.par.hmode = b.par.vmode = 'fill'
        b.par.bgalpha = 1
        active = f'({state} == {i})'
        for ch, accent, base in (
            ('bgcolorr', 'Btnaccr', 'Btnr'),
            ('bgcolorg', 'Btnaccg', 'Btng'),
            ('bgcolorb', 'Btnaccb', 'Btnb'),
        ):
            _expr(getattr(b.par, ch),
                  f'(parent.tool.par.{accent} if {active} else parent.tool.par.{base}) '
                  f'* (1.2 if me.panel.inside else 1.0)')
        b.par.borderaalpha = 0
        b.par.cursor = 'pointer'

        l = b.create(textCOMP, 'lbl')
        l.par.hmode = l.par.vmode = 'fill'
        l.par.bgalpha = 0
        l.par.fontsize, l.par.fontsizeunits = 11, 'panelunits'
        l.par.scaletofit = 'never'
        l.par.alignx, l.par.alignxmode = 'center', 'metrics'
        l.par.aligny, l.par.alignymode = 'center', 'bbox'
        l.par.bold = True
        l.par.text = lab
        _ink(l)
    return seg


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------
PANEL_CALLBACKS_SOURCE = '''"""
Panel Execute DAT — dispatcher for all CollectTDProject panel buttons.

Owner-name based dispatch.
- Toggles + segmented buttons fire on press (offtoon) for snappy feel.
- Main pulse buttons (FIND/CONSOLIDATE/UNDO/CLEAR) fire on release-inside,
  with cancel-on-drag-out.
"""

from typing import Any

_TOGGLES = {
    "tgl_modparam": "Modifyparams",
    "tgl_palette":  "Ignorepalettecomps",
}
_INDEXED = {
    "seg_conflict_": "Conflictstrategy",
    "seg_mode_":     "Movefiles",
}


def _dispatch_press(panelValue):
    tool = parent.tool
    name = panelValue.owner.name
    if name in _TOGGLES:
        p = getattr(tool.par, _TOGGLES[name])
        p.val = 0 if p.eval() else 1
        return
    for prefix, par_name in _INDEXED.items():
        if name.startswith(prefix):
            try:
                idx = int(name[len(prefix):])
            except ValueError:
                return
            getattr(tool.par, par_name).val = idx
            return


def _dispatch_release(panelValue):
    if not panelValue.owner.panel.inside:
        return
    tool = parent.tool
    name = panelValue.owner.name
    if name == "btn_find":
        tool.par.Findfiles.pulse()
    elif name == "btn_consolidate":
        tool.par.Consolidatefiles.pulse()
    elif name == "btn_undo":
        tool.par.Undo.pulse()
    elif name == "btn_clear":
        tool.par.Clearlog.pulse()
    elif name == "btn_instagram":
        import webbrowser
        webbrowser.open("https://www.instagram.com/lumalux_3dmapping/")


def onOffToOn(panelValue):    _dispatch_press(panelValue)
def onOnToOff(panelValue):    _dispatch_release(panelValue)
def whileOn(panelValue):      return
def whileOff(panelValue):     return
def onValueChange(panelValue, prev): return
'''


def run():
    tool = parent.tool
    ui = tool.op('ui')

    # tear down previous build
    old = ui.op('config')
    if old:
        old.destroy()

    # build container
    cfg = ui.create(containerCOMP, 'config')
    cfg.par.alignorder = 0.5  # between actions(0) and status(1)
    cfg.par.hmode, cfg.par.vmode = 'fill', 'fixed'
    cfg.par.h = ROW_H * 7 + 70 + SPACING * 7 + 16
    cfg.par.align, cfg.par.spacing = 'verttb', SPACING
    cfg.par.marginl = cfg.par.marginr = 0
    cfg.par.margint = cfg.par.marginb = 4
    cfg.par.bgalpha = 1
    _expr(cfg.par.bgcolorr, 'parent.tool.par.Bgaltr')
    _expr(cfg.par.bgcolorg, 'parent.tool.par.Bgaltg')
    _expr(cfg.par.bgcolorb, 'parent.tool.par.Bgaltb')
    cfg.par.borderaalpha = 0

    rows = [
        ('row_scanroot', 'Scan Root',      lambda r: _make_text_input(r, 'tin_scanroot', 'parent.tool.par.Scanroot')),
        ('row_maxdepth', 'Max Depth',      lambda r: _make_text_input(r, 'tin_maxdepth', 'parent.tool.par.Maxdepth', type_='integer', w=72)),
        ('row_mode',     'Mode',           lambda r: _make_segmented(r, 'seg_mode',     'parent.tool.par.Movefiles',         MODE_LABELS,     par_kind='int')),
        ('row_conflict', 'Conflict',       lambda r: _make_segmented(r, 'seg_conflict', 'parent.tool.par.Conflictstrategy',  CONFLICT_LABELS, par_kind='menu')),
        ('row_modparam', 'Rewrite Params', lambda r: _make_toggle(r, 'tgl_modparam', 'parent.tool.par.Modifyparams')),
        ('row_palette',  'Ignore Palette', lambda r: _make_toggle(r, 'tgl_palette',  'parent.tool.par.Ignorepalettecomps')),
        ('row_xtypes',   'Exclude Types',  lambda r: _make_text_input(r, 'tin_xtypes', 'parent.tool.par.Excludefiletypes')),
        ('row_xcomps',   'Exclude COMPs',  lambda r: _make_text_input(r, 'tin_xcomps', 'parent.tool.par.Excludecomps', multiline=True)),
    ]
    for i, (rname, label, builder) in enumerate(rows):
        h = 70 if rname == 'row_xcomps' else ROW_H
        r = _make_row(cfg, rname, alignorder=i, h=h)
        _make_label(r, 'lbl', label)
        builder(r)

    # rewire panel_callbacks: glob + dispatch
    pc = ui.op('panel_callbacks')
    pc.par.panels.expr = (
        "parent.tool.op('ui/actions') + '/* ' + "
        "parent.tool.op('ui/log_view/btn_clear') + ' ' + "
        "parent.tool.op('ui/footer/btn_instagram') + ' ' + "
        "parent.tool.op('ui/config') + '/*/tgl_* ' + "
        "parent.tool.op('ui/config') + '/*/seg_*/* '"
    )
    pc.par.panels.mode = ParMode.EXPRESSION
    pc.par.offtoon = True
    pc.par.ontooff = True
    pc.text = PANEL_CALLBACKS_SOURCE

    # status bar can shrink instead of clipping at narrow widths
    ui.op('status').par.scaletofit = 'onlyshrink'

    # mirror network tile to panel aspect for visible-on-canvas debugging
    try:
        cfg.resetNodeSize()
    except Exception:
        pass

    print(f'[build_panel] config built; {len(cfg.findChildren(depth=999))} ops in cfg')

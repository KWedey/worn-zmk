#!/usr/bin/env python3
"""Regenerate keymap.html's layer tables from worn.keymap.

The page duplicates every binding, so hand-editing both drifts. Run this
after any keymap change; it rewrites the const L0..L3 arrays in place.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KEYMAP = ROOT / "boards/shields/worn/worn.keymap"
PAGE = ROOT / "keymap.html"
LAYERS = ["default_layer", "lower_layer", "raise_layer", "3"]

SPECIAL = {
    "ESC": ("ESC", "f"), "TAB": ("TAB", "f"), "BSPC": ("BSPC", "f"),
    "DEL": ("DEL", "f"), "RET": ("ENTER", "f"), "SPACE": ("SPACE", "f"),
    "LCTRL": ("CTRL", "m"), "RCTRL": ("CTRL", "m"), "LSHFT": ("SHIFT", "m"),
    "RSHFT": ("SHIFT", "m"), "LGUI": ("CMD", "m"), "RGUI": ("CMD", "m"),
    "LALT": ("ALT", "m"), "RALT": ("ALT", "m"),
    "LEFT": ("←", "n"), "RIGHT": ("→", "n"),
    "UP": ("↑", "n"), "DOWN": ("↓", "n"),
    "SEMI": (";", "a"), "SQT": ("'", "a"), "COMMA": (",", "a"),
    "DOT": (".", "a"), "FSLH": ("/", "a"),
    "EXCL": ("!", "s"), "AT": ("@", "s"), "HASH": ("#", "s"),
    "DLLR": ("$", "s"), "PRCNT": ("%", "s"), "CARET": ("^", "s"),
    "AMPS": ("&", "s"), "ASTRK": ("*", "s"), "LPAR": ("(", "s"),
    "RPAR": (")", "s"), "MINUS": ("-", "s"), "EQUAL": ("=", "s"),
    "LBKT": ("[", "s"), "RBKT": ("]", "s"), "BSLH": ("\\", "s"),
    "GRAVE": ("`", "s"), "UNDER": ("_", "s"), "PLUS": ("+", "s"),
    "LBRC": ("{", "s"), "RBRC": ("}", "s"), "PIPE": ("|", "s"),
    "TILDE": ("~", "s"),
}
LAYER_NAMES = {"1": "LOWER", "2": "RAISE", "3": "TRI"}


def describe(binding):
    """Map a ZMK binding to the page's (label, kind) pair."""
    if binding == "&trans":
        return None
    if binding.startswith("&kp "):
        code = binding[4:]
        if code in SPECIAL:
            return SPECIAL[code]
        if re.fullmatch(r"[A-Z]", code):
            return code, "a"
        if re.fullmatch(r"N\d", code):
            return code[1], "d"
        if re.fullmatch(r"F\d{1,2}", code):
            return code, "f"
    if binding.startswith("&mo "):
        n = binding[4:]
        return LAYER_NAMES.get(n, "L" + n), "l"
    if binding == "&bt BT_CLR":
        return "BT CLR", "b"
    m = re.fullmatch(r"&bt BT_SEL (\d)", binding)
    if m:
        return "BT " + m.group(1), "b"
    raise SystemExit(f"sync-keymap-html: no label for {binding!r} -- add it to SPECIAL")


def read_layer(src, name):
    m = re.search(re.escape(name) + r"\s*\{.*?bindings = <(.*?)>;", src, re.S)
    if not m:
        raise SystemExit(f"sync-keymap-html: layer {name!r} not found")
    toks = [re.sub(r"\s+", " ", t.strip())
            for t in re.findall(r"&\w+(?:\s+[A-Z0-9_]+)*", m.group(1))]
    if len(toks) != 42:
        raise SystemExit(f"sync-keymap-html: layer {name!r} has {len(toks)} bindings, expected 42")
    return toks


def render(toks):
    rows = []
    for r in range(4):
        span = toks[36:42] if r == 3 else toks[r * 12:(r + 1) * 12]
        cells = []
        for b in span:
            d = describe(b)
            cells.append("T" if d is None
                         else f"[{json.dumps(d[0])},{json.dumps(b)},{json.dumps(d[1])}]")
        rows.append(" " + ",".join(cells) + ",")
    return "\n".join(rows).rstrip(",")


def main():
    src = KEYMAP.read_text()
    page = PAGE.read_text()
    changed = []
    for n, layer in enumerate(LAYERS):
        block = f"const L{n}=[\n{render(read_layer(src, layer))}];"
        new, count = re.subn(rf"const L{n}=\[.*?\];", lambda m: block, page, flags=re.S)
        if count != 1:
            raise SystemExit(f"sync-keymap-html: expected one const L{n} block, found {count}")
        if new != page:
            changed.append(f"L{n} ({layer})")
        page = new
    PAGE.write_text(page)
    print("synced: " + (", ".join(changed) if changed else "no changes"))


if __name__ == "__main__":
    main()

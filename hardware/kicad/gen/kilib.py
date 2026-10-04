"""KiCad file helpers shared by the generators: s-expressions and stock symbol lookup."""
import copy
import re
from pathlib import Path

SHARE = Path("/Applications/KiCad/KiCad.app/Contents/SharedSupport")
_LIB_TEXT = {}


class Q(str):
    """A quoted s-expression string (kept distinct from bare atoms when written back out)."""


def parse(text):
    stack, i, n = [[]], 0, len(text)
    while i < n:
        c = text[i]
        if c in " \t\r\n":
            i += 1
        elif c == "(":
            stack.append([])
            i += 1
        elif c == ")":
            done = stack.pop()
            stack[-1].append(done)
            i += 1
        elif c == '"':
            j = i + 1
            while text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            stack[-1].append(Q(text[i + 1:j]))
            i = j + 1
        else:
            j = i
            while j < n and text[j] not in " \t\r\n()":
                j += 1
            stack[-1].append(text[i:j])
            i = j
    return stack[0][0]


def dump(node, depth=0):
    if isinstance(node, Q):
        return '"' + node + '"'
    if isinstance(node, float):
        return ("%.4f" % node).rstrip("0").rstrip(".")
    if not isinstance(node, list):
        return str(node)
    if all(not isinstance(c, list) for c in node):
        return "(" + " ".join(dump(c) for c in node) + ")"
    out, seen_list = "(", False
    for k, c in enumerate(node):
        if isinstance(c, list) or seen_list:
            seen_list = True
            out += "\n" + "\t" * (depth + 1) + dump(c, depth + 1)
        else:
            out += ("" if k == 0 else " ") + dump(c)
    return out + "\n" + "\t" * depth + ")"


def child(node, key):
    return next((c for c in node if isinstance(c, list) and c and c[0] == key), None)


def children(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def load_symbol(lib, name):
    """Return a stock symbol's s-expression with any (extends ...) parent merged in."""
    if lib not in _LIB_TEXT:
        _LIB_TEXT[lib] = (SHARE / "symbols" / (lib + ".kicad_sym")).read_text()
    text = _LIB_TEXT[lib]
    m = re.search(r'^\t\(symbol "%s"\s*$' % re.escape(name), text, re.M)
    if m is None:
        raise KeyError("symbol %s:%s not in the stock libraries" % (lib, name))
    nxt = re.compile(r'^\t\(symbol "', re.M).search(text, m.end())
    node = parse(text[m.start():nxt.start() if nxt else text.rindex(")")])
    ext = child(node, "extends")
    if ext is None:
        return node
    parent_name = str(ext[1])
    parent = load_symbol(lib, parent_name)
    mine = {str(c[1]): c for c in children(node, "property")}
    out = []
    for c in parent:
        if isinstance(c, list) and c[0] == "property" and str(c[1]) in mine:
            out.append(mine.pop(str(c[1])))
        elif isinstance(c, list) and c[0] == "symbol":
            c = copy.deepcopy(c)
            c[1] = Q(str(c[1]).replace(parent_name, name, 1))
            out.append(c)
        else:
            out.append(c)
    out[1] = Q(name)
    first_unit = next((k for k, c in enumerate(out) if isinstance(c, list) and c[0] == "symbol"), len(out))
    out[first_unit:first_unit] = list(mine.values())
    return out


def symbol_pins(sym):
    """List of dicts: number, name, x, y, angle, etype, unit (0 = common to all units)."""
    pins = []
    for unit in children(sym, "symbol"):
        unit_no = int(str(unit[1]).rsplit("_", 2)[-2])
        for p in children(unit, "pin"):
            at = child(p, "at")
            pins.append(dict(number=str(child(p, "number")[1]), name=str(child(p, "name")[1]), etype=str(p[1]),
                             x=float(at[1]), y=float(at[2]), angle=int(float(at[3])) if len(at) > 3 else 0, unit=unit_no))
    return pins


def symbol_property(sym, name):
    for p in children(sym, "property"):
        if str(p[1]) == name:
            return str(p[2])
    return ""

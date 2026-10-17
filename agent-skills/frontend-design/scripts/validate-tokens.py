#!/usr/bin/env python3
"""Validate this opt-in token seed using only the Python standard library."""

import argparse
import copy
import itertools
import json
from pathlib import Path
import re
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def css_rules(css, contexts=()):
    """Parse the shipped subset: scoped declaration blocks and nested media rules."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = []
    pos = 0
    while css[pos:].strip():
        start = css.find("{", pos)
        require(start >= 0, "Unexpected CSS trailing content")
        header = re.sub(r"\s+", " ", css[pos:start]).strip()
        level, end = 1, start + 1
        while end < len(css) and level:
            level += (css[end] == "{") - (css[end] == "}")
            end += 1
        require(level == 0, "Unbalanced CSS braces")
        body = css[start + 1:end - 1]
        if header.startswith("@media "):
            rules.extend(css_rules(body, contexts + (header[7:],)))
        else:
            values = {}
            for declaration in body.split(";"):
                if not declaration.strip():
                    continue
                require(":" in declaration, "Invalid CSS declaration")
                key, value = (part.strip() for part in declaration.split(":", 1))
                require(key not in values, f"Duplicate CSS declaration: {key}")
                values[key] = value
            rules.append((contexts, header, values))
        pos = end
    return rules


def luminance(color):
    require(bool(re.fullmatch(r"#[0-9a-fA-F]{6}", color)), f"Expected sRGB hex: {color}")
    channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
              for v in channels]
    return sum(v * w for v, w in zip(linear, (0.2126, 0.7152, 0.0722)))


def contrast(a, b):
    lo, hi = sorted((luminance(a), luminance(b)))
    return (hi + 0.05) / (lo + 0.05)


def validate(data, css):
    require(data["schemaVersion"] == 1 and data["prefix"] == "fd", "Unknown token schema")
    common, themes, prefs = data["common"], data["themes"], data["preferences"]
    require(set(themes) == {"light", "dark"}, "Expected light/dark themes")
    require(set(themes["light"]) == set(themes["dark"]), "Theme roles differ")
    require(not set(common) & set(themes["light"]), "Common/theme keys overlap")
    require(set(prefs) == {"more-contrast", "reduced-motion", "forced-colors"},
            "Unexpected preference branches")
    require(set(prefs["forced-colors"]) == set(themes["light"]), "Forced-color roles differ")
    for name, branch in prefs["more-contrast"].items():
        require(name in themes and set(branch) <= set(themes[name]), "Invalid contrast roles")
    require(set(prefs["more-contrast"]) == set(themes), "Contrast themes differ")
    require(set(prefs["reduced-motion"]) <= set(common), "Invalid reduced-motion roles")
    known = set(common) | set(themes["light"])

    def variables(values):
        require(all(re.fullmatch(r"[a-z][a-z0-9-]*", k) and isinstance(v, str) and v
                    for k, v in values.items()), "Invalid token key/value")
        return {f"--fd-{k}": v for k, v in values.items()}

    base, dark, auto = "[data-fd-theme]", '[data-fd-theme="dark"]', '[data-fd-theme="auto"]'
    dark_query = "(prefers-color-scheme: dark)"
    more_query = "(prefers-contrast: more)"
    reduce_query = "(prefers-reduced-motion: reduce)"
    forced_query = "(forced-colors: active)"
    expected = [
        ((), base, variables({**common, **themes["light"]})),
        ((), base, {"color-scheme": "var(--fd-color-scheme)"}),
        ((), dark, variables(themes["dark"])),
        ((dark_query,), auto, variables(themes["dark"])),
        ((), base + ":focus-visible, " + base + " :focus-visible", {
            "outline": "var(--fd-focus-width) solid var(--fd-color-focus)",
            "outline-offset": "var(--fd-focus-offset)"}),
        ((more_query,), base, variables(prefs["more-contrast"]["light"])),
        ((more_query,), dark, variables(prefs["more-contrast"]["dark"])),
        ((more_query + " and " + dark_query,), auto, variables(prefs["more-contrast"]["dark"])),
        ((reduce_query,), base, variables(prefs["reduced-motion"])),
        ((forced_query,), base, variables(prefs["forced-colors"])),
        ((forced_query,), base, {"forced-color-adjust": "auto"}),
    ]
    actual = css_rules(css)
    require(actual == expected, "CSS selectors, media branches, order or values differ from JSON contract")
    refs = set(re.findall(r"var\(--fd-([a-z0-9-]+)\)", css))
    require(refs <= known, f"Undefined CSS variables: {sorted(refs - known)}")

    # Enumerate the equal-specificity token cascade, not a full browser CSS engine.
    cases = 0
    for selected, system_dark, more, reduced, forced in itertools.product(
            ("light", "dark", "auto"), (False, True), (False, True), (False, True), (False, True)):
        theme = "dark" if selected == "dark" or selected == "auto" and system_dark else "light"
        resolved = {**common, **themes[theme]}
        if more:
            resolved.update(prefs["more-contrast"][theme])
        if reduced:
            resolved.update(prefs["reduced-motion"])
        if forced:
            resolved.update(prefs["forced-colors"])
        calculated = {}
        for contexts, selector, values in actual:
            if selector not in (base, dark, auto):
                continue
            if selector == dark and selected != "dark" or selector == auto and selected != "auto":
                continue
            flags = {dark_query: system_dark, more_query: more, reduce_query: reduced, forced_query: forced}
            if not all(all(flags[term] for term in query.split(" and ")) for query in contexts):
                continue
            calculated.update({k[5:]: v for k, v in values.items() if k.startswith("--fd-")})
        require(calculated == resolved, f"Theme cascade mismatch: {selected, system_dark, more, reduced, forced}")
        cases += 1

    ratios = {"text": [], "non-text": []}
    for theme, more in itertools.product(themes, (False, True)):
        colors = {**themes[theme], **(prefs["more-contrast"][theme] if more else {})}
        pairs = []
        for surface in ("color-bg", "color-surface", "color-surface-raised"):
            pairs.extend((role, surface, 4.5, "text") for role in ("color-text", "color-muted", "color-accent"))
            pairs.extend((role, surface, 3.0, "non-text") for role in ("color-border", "color-focus"))
        pairs.extend(("color-on-accent", role, 4.5, "text")
                     for role in ("color-accent", "color-accent-hover"))
        pairs.extend((f"color-{role}", f"color-{role}-bg", 4.5, "text")
                     for role in ("success", "warning", "danger", "info"))
        for fg, bg, minimum, kind in pairs:
            ratio = contrast(colors[fg], colors[bg])
            require(ratio >= minimum, f"Low contrast: {theme}/{more} {fg}/{bg} {ratio:.3f} < {minimum}")
            ratios[kind].append(ratio)
    return cases, ratios


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Also test two deliberately broken seeds")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root / "assets/design-tokens.json").read_text())
    css = (root / "assets/design-tokens.css").read_text()
    cases, ratios = validate(data, css)
    print(f"PASS JSON/CSS branch parity and {cases} theme/preference cascades")
    for kind, values in ratios.items():
        print(f"PASS {kind}: {len(values)} color pairs; minimum contrast {min(values):.3f}:1")
    if args.self_test:
        mutations = [(data, css.replace("--fd-space-1: 0.25rem;", "--fd-space-1: 9rem;", 1))]
        low = copy.deepcopy(data)
        low["themes"]["light"]["color-muted"] = "#ffffff"
        mutations.append((low, css.replace("--fd-color-muted: #526071;", "--fd-color-muted: #ffffff;", 1)))
        for broken_data, broken_css in mutations:
            try:
                validate(broken_data, broken_css)
            except ValueError:
                continue
            raise ValueError("Mutation unexpectedly passed validation")
        print("PASS negative tests: CSS drift and synchronized low-contrast seed rejected")
    print("NOT VERIFIED: browser CSS rendering, OS system-color contrast, screen readers, real devices")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        sys.exit(1)

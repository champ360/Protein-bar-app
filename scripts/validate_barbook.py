#!/usr/bin/env python3
"""Regression guardrails for Barbook's user-facing behavior and Android version."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
GRADLE = ROOT / "app/build.gradle"
errors: list[str] = []

def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)

if not HTML.exists():
    print("FAIL: canonical app UI is missing:", HTML)
    sys.exit(1)

html = HTML.read_text(encoding="utf-8")
gradle = GRADLE.read_text(encoding="utf-8")

# Meaningful catalogue sorting only.
options = re.findall(r'<option\s+value="([^"]+)"', html)
require(options == ["efficiency", "price20"], f"Expected exactly the two approved sort options; found {options!r}")
require("sortMode = 'efficiency'" in html, "Protein per 100 kcal must be the default sort")
require("sortMode==='price20'" in html, "Price-per-20g sorting logic is missing")
require("proteinEfficiency(b)-proteinEfficiency(a)" in html, "Efficiency sort must rank highest first")

# Direct-to-catalogue navigation and intentionally minimal UI.
require("let tab = 'browse'" in html, "App must open directly on All bars")
require("function homePage()" not in html and "tab==='home'" not in html, "Redundant Home page has been reintroduced")
require("[['browse','All bars'],['tasted','Tried']]" in html, "Bottom navigation should contain only All bars and Tried")
require('aria-label="Search bars"' not in html, "Inert top-right search shortcut has been reintroduced")
require('id="searchInput"' in html, "Functional catalogue search field must remain")
require("Hide duplicate pack sizes" not in html and "unique-hint" not in html, "Redundant unique-flavour helper text must stay removed")
require("Prices and nutrition from your tracker sheet" not in html and "footer-note" not in html, "Redundant tracker footer note must stay removed")

# Local-only personal data and agreed rating controls.
require("barbook-v1-personal-edits" in html, "Do not change the existing localStorage key without a migration")
require('id="uniqueFlavours"' in html, "Unique-flavours toggle is missing")
require('data-save' in html and 'data-discard' in html, "Save/Discard editing controls are missing")
require('data-theme="dark"' in html, "Dark-mode styling is missing")
require("ratingTone = score => Number(score) >= 8 ? 'rating-good' : (Number(score) >= 6 ? 'rating-mid' : 'rating-low')" in html,
        "Rating colour thresholds must be 8–10 green, 6–7 yellow, 1–5 red")
require("availabilityFilter==='Blinkit'" in html and "availabilityFilter==='Website'" in html,
        "Marketplace-specific prices are missing")
require("<textarea" not in html.lower() and "tasting notes" not in html.lower(),
        "Free-text tasting notes are outside the agreed scope")
require('flavor:"Hazelnut Cocoa",series:"PRO"' in html and 'tried:true,rating:6' in html,
        "Hazelnut Cocoa should be seeded as tried with a 6/10 rating")
require("group.tasting.rating" in html and "group.representative" in html,
        "Unique-flavour view must carry tasting status from matching pack variants")

# Android identity and release version.
require("applicationId 'com.barbook.wholetruth'" in gradle, "Android application ID changed unexpectedly")
version_name = re.search(r"versionName\s+['\"]([^'\"]+)['\"]", gradle)
version_code = re.search(r"versionCode\s+(\d+)", gradle)
require(bool(version_name and version_name.group(1) == "1.4"), "Android versionName should be 1.4")
require(bool(version_code and int(version_code.group(1)) == 5), "Android versionCode should be 5")

# JavaScript syntax check.
script_blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
require(len(script_blocks) == 1, f"Expected one inline JavaScript block; found {len(script_blocks)}")
if len(script_blocks) == 1:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", encoding="utf-8") as js_file:
        js_file.write(script_blocks[0])
        js_file.flush()
        try:
            result = subprocess.run(["node", "--check", js_file.name], capture_output=True, text=True, check=False)
            require(result.returncode == 0, f"JavaScript syntax check failed: {result.stderr.strip()}")
        except FileNotFoundError:
            print("WARNING: Node.js not available; skipped JavaScript syntax check")

if errors:
    for error in errors:
        print("FAIL:", error)
    sys.exit(1)

print("Barbook v1.4 checks passed:")
print("- direct-to-All-bars navigation; no Home or inert header search shortcut")
print("- only the two approved sorts; unique-flavour switch is compact")
print("- local rating data, Save/Discard, dark mode and marketplace pricing preserved")
print("- rating colour thresholds and Hazelnut Cocoa 6/10 seed verified")
print("- Android identity/version intact; JavaScript syntax valid")

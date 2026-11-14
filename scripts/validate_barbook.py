#!/usr/bin/env python3
"""Regression guardrails for Barbook's user-facing behaviour, rendering rules, signing and version."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
GRADLE = ROOT / "app/build.gradle"
JAVA = ROOT / "app/src/main/java/com/barbook/wholetruth/MainActivity.java"
KEYSTORE = ROOT / "signing/barbook.keystore"
WORKFLOWS = ROOT / ".github/workflows"
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def function_body(source: str, name: str) -> str:
    """Return the text of a top-level `function name(...) { ... }` by matching braces."""
    match = re.search(r"function\s+" + re.escape(name) + r"\s*\([^)]*\)\s*\{", source)
    if not match:
        return ""
    depth, i = 1, match.end()
    while i < len(source) and depth:
        depth += {"{": 1, "}": -1}.get(source[i], 0)
        i += 1
    return source[match.end():i]


for path in (HTML, GRADLE, JAVA):
    if not path.exists():
        print("FAIL: required file is missing:", path)
        sys.exit(1)

html = HTML.read_text(encoding="utf-8")
gradle = GRADLE.read_text(encoding="utf-8")
java = JAVA.read_text(encoding="utf-8")

# --- Meaningful catalogue sorting only.
options = re.findall(r'<option\s+value="([^"]+)"', html)
require(options == ["efficiency", "price20"], f"Expected exactly the two approved sort options; found {options!r}")
require("sortMode = 'efficiency'" in html, "Protein per 100 kcal must be the default sort")
require("sortMode==='price20'" in html, "Price-per-20g sorting logic is missing")
require("proteinEfficiency(b)-proteinEfficiency(a)" in html, "Efficiency sort must rank highest first")
require("Protein / 100 kcal · high to low" in html and "₹ / 20g protein · low to high" in html, "Sort labels must read 'high to low' and 'low to high'")
require("highest first" not in html and "lowest first" not in html, "Sort labels must not say 'highest first' or 'lowest first'")

# --- Direct-to-catalogue navigation and intentionally minimal UI.
require("tab = 'browse'" in html, "App must open directly on All bars")
require("function homePage()" not in html and "tab==='home'" not in html, "Redundant Home page has been reintroduced")
require("[['browse','All bars'],['tasted','Tried']]" in html, "Bottom navigation should contain only All bars and Tried")
require('aria-label="Search bars"' not in html, "Inert top-right search shortcut has been reintroduced")
require('id="searchInput"' in html, "Functional catalogue search field must remain")
require("Hide duplicate pack sizes" not in html and "unique-hint" not in html, "Redundant unique-flavour helper text must stay removed")
require("Prices and nutrition from your tracker sheet" not in html and "footer-note" not in html, "Redundant tracker footer note must stay removed")
require("sort-helper" not in html and "Only meaningful comparisons" not in html, "The sort helper sentence must stay removed")
require('data-action="theme"' not in html, "Dark mode lives only in Settings; do not put a theme button back in the header")
require("serviceWorker" not in html, "The service-worker registration is dead code in the Android WebView; do not reintroduce it")

# --- Local-only personal data and agreed rating controls.
require("barbook-v1-personal-edits" in html, "Do not change the existing localStorage key without a migration")
require('id="uniqueFlavours"' in html, "Unique-flavours toggle is missing")
require("data-save" in html and "data-discard" in html, "Save/Discard editing controls are missing")
require('data-theme="dark"' in html, "Dark-mode styling is missing")
require("ratingTone = score => Number(score) >= 8 ? 'rating-good' : (Number(score) >= 6 ? 'rating-mid' : 'rating-low')" in html,
        "Rating colour thresholds must be 8–10 green, 6–7 yellow, 1–5 red")
require("availabilityFilter==='Blinkit'" in html and "availabilityFilter==='Website'" in html, "Marketplace-specific prices are missing")
require("<textarea" not in html.lower() and "tasting notes" not in html.lower(), "Free-text tasting notes are outside the agreed scope")
require('flavor:"Hazelnut Cocoa",series:"PRO"' in html and "tried:true,rating:6" in html, "Hazelnut Cocoa should be seeded as tried with a 6/10 rating")
require("proteinEfficiency(b)>proteinEfficiency(old)" in html, "Unique flavours must keep the variant with the highest protein per 100 kcal")
require("group.tasting.rating" in html and "group.representative" in html, "Unique-flavour view must carry tasting status from matching pack variants")
require(len(re.findall(r"\{id:\d+,flavor:", html)) == 23, "The catalogue should contain exactly 23 bars unless a data change was requested")

# --- Dark mode: no light flash, no light line.
require("var(--nav-line)" in html and "rgba(225,222,216,.8)" not in re.search(r"\.bottom-nav\s*\{[^}]*\}", html).group(0),
        "The bottom bar border must use the themed --nav-line variable (a fixed light colour shows as a white line in dark mode)")
require("html.preload" in html and "localStorage.getItem('barbook-theme-v1')" in html.split("</head>")[0], "The saved theme must be applied in <head> before first paint")
require("getSharedPreferences" in java and "onResume" in java and "setBackgroundDrawable" in java, "MainActivity must remember the theme and apply it at start and resume (prevents a white flash in dark mode)")

# --- Theme: Light, Dark or System.
require(all(f'data-theme-set="${{id}}"' in html or id in html for id in ("light", "dark", "system")) and "[['light','Light'],['dark','Dark'],['system','System']]" in html, "Settings must offer Light, Dark and System themes")
require("prefers-color-scheme: dark" in html and "normalizeThemePref" in html, "The System theme must follow the phone's colour scheme")
require("setThemeMode" in java and "uiMode" in (ROOT / "app/src/main/AndroidManifest.xml").read_text(encoding="utf-8"), "MainActivity must resolve the System theme and handle uiMode changes")
require((ROOT / "app/src/main/res/values-night/styles.xml").exists(), "values-night/styles.xml is needed so the start-up window is dark when the phone is dark")

# --- Settings, export and import.
require("data-export" in html and "data-import" in html, "Settings must offer Export and Import")
require("window.BarbookNative.saveBackup" in html and "window.BarbookNative.pickBackup" in html, "Export/Import must use the Android file bridge")
require("function onBackupPicked" in html and "function parseBackup" in html and "function cleanEdits" in html, "Import must parse and sanitise backup files")
require("@JavascriptInterface" in java and "saveBackup" in java and "pickBackup" in java and "onActivityResult" in java,
        "MainActivity must implement the backup file bridge")

# --- No flashing: the screen must not be rebuilt or re-animated on ordinary taps.
sheet_rules = re.findall(r"\n\s*\.sheet\s*\{([^}]*)\}", html)
require(sheet_rules and all("animation" not in rule for rule in sheet_rules), "`.sheet` must not animate by default (use `.sheet.enter`)")
backdrop_rules = re.findall(r"\n\s*\.modal-backdrop\s*\{([^}]*)\}", html)
require(backdrop_rules and all("animation" not in rule for rule in backdrop_rules), "`.modal-backdrop` must not animate by default (use `.modal-backdrop.enter`)")
require(".sheet.enter" in html and ".modal-backdrop.enter" in html, "Sheet entrance animation must be limited to the `.enter` class")
require(not re.search(r"\n\s*main\s*\{[^}]*animation", html), "The page container must not replay an entrance animation")
require("modalRoot').innerHTML" not in function_body(html, "renderDetails"), "renderDetails must patch the open sheet, not replace it")
require(not re.search(r"\brender\(\)", function_body(html, "saveDraft")), "Saving must not rebuild the whole page")
require(not re.search(r"\brender\(\)", function_body(html, "switchTab")), "Switching tabs must not rebuild the header")

# --- Android identity, version and signing.
require("applicationId 'com.barbook.wholetruth'" in gradle, "Android application ID changed unexpectedly")
version_name = re.search(r"versionName\s+['\"]([^'\"]+)['\"]", gradle)
version_code = re.search(r"versionCode\s+(\d+)", gradle)
app_version = re.search(r"const APP_VERSION = '([^']+)'", html)
require(bool(version_name), "versionName missing in app/build.gradle")
require(bool(version_code), "versionCode missing in app/build.gradle")
require(bool(app_version and version_name and app_version.group(1) == version_name.group(1)),
        "APP_VERSION in index.html must match versionName in app/build.gradle")
require(KEYSTORE.exists() and KEYSTORE.stat().st_size > 0, "The fixed signing keystore signing/barbook.keystore is missing")
require("signingConfigs" in gradle and re.search(r"release\s*\{[^}]*signingConfig signingConfigs\.barbook", gradle, re.S) is not None,
        "The release build must use signingConfigs.barbook so updates install over earlier versions")
for workflow in sorted(WORKFLOWS.glob("*.yml")):
    text = workflow.read_text(encoding="utf-8")
    require("assembleDebug" not in text, f"{workflow.name} must build the signed release APK, not a debug APK")

# --- JavaScript syntax check.
script_blocks = re.findall(r"<script>(.*?)</script>", html, re.S)
require(len(script_blocks) == 2, f"Expected the small theme script in <head> plus one app script; found {len(script_blocks)} inline blocks")
if script_blocks:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", encoding="utf-8") as js_file:
        js_file.write("\n;\n".join(script_blocks))
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

print(f"Barbook v{version_name.group(1)} checks passed:")
print("- direct-to-All-bars navigation; no Home, inert search shortcut or dead service worker")
print("- two approved sorts; compact unique-flavours switch; catalogue intact")
print("- rating colours, Hazelnut Cocoa 6/10 seed, local-only data, Save/Discard, dark mode")
print("- Settings with export/import wired to the Android file bridge; dark mode only in Settings")
print("- dark mode: themed bottom-bar border, saved theme applied before first paint and at app start/resume")
print("- no entrance animations or full re-renders on ordinary taps")
print("- fixed signing key, signed release build, versions in sync; JavaScript syntax valid")

# Barbook v1.4

A lightweight, offline-first Android tracker for The Whole Truth protein bars.

## Current product behaviour

- App opens directly on **All bars**; there is no Home page.
- Bottom navigation contains only **All bars** and **Tried**.
- The redundant top-right search shortcut is removed; the working search field stays in All bars.
- A compact **Unique flavours** switch collapses pack/series variants with matching flavour names.
- Sort options are only protein per 100 kcal (default, highest first) and ₹ per 20g protein (lowest first).
- Marketplace price follows the selected marketplace filter; Any shows the lower available price and its source.
- Personal status is limited to tried/not tried and an optional rating from 1 to 10.
- Ratings 8–10 are green, 6–7 yellow, and 1–5 red.
- Personal data is local only. No cloud sync, accounts, remote databases, analytics, or data upload.
- Existing records remain in `localStorage` under `barbook-v1-personal-edits`.

## Project structure

- `app/src/main/assets/index.html` — canonical app UI and product data (single source of truth).
- `app/src/main/java/com/barbook/wholetruth/MainActivity.java` — Android WebView wrapper.
- `app/src/main/res/` — required launcher and Android resources.
- `.github/copilot-instructions.md` — persistent rules for Copilot coding agent.
- `.github/prompts/barbook-feature.prompt.md` — reusable feature-task prompt.
- `.github/workflows/build-apk.yml` — builds APK and runs regression checks on PRs, main-branch pushes and manual runs.
- `scripts/validate_barbook.py` — lightweight regression checks.

## Making changes with Copilot

Use GitHub Copilot **Coding agent** on this existing repository. Ask it to make a change and open a pull request; do not ask it to push directly to `main`. Copilot should follow `.github/copilot-instructions.md`, run `python scripts/validate_barbook.py`, and let GitHub Actions build the APK on the pull request. Review and approve/merge the pull request; the build artifact is then available in Actions.

You do not upload this ZIP into Copilot. This ZIP is an optional complete project snapshot/backup. When using Copilot Agent on the live repository, prompt the agent in GitHub; it edits the repository branch and creates the pull request for review.

## Build APK

After a successful Actions run, download the `barbook-v1.4-debug-apk` artifact and extract `app-debug.apk`.

**Signing warning:** This project still builds a debug APK. Installing updates over an existing installation requires the same signing certificate. Configure a persistent signing key in GitHub Actions Secrets before relying on in-place APK upgrades. Do not uninstall the current working app or change its signing identity before signing is configured and verified.

## Data and privacy

Tried status and ratings remain on the device in WebView localStorage. Do not rename or clear the storage key. The catalogue seeds Hazelnut Cocoa (PRO, 20g) as Tried · 6/10 as requested. In unique-flavour mode, a rating recorded on any matching pack-size variant is reflected on the displayed representative. There is no cloud sync, remote database, login, analytics, or data upload.

# Barbook v1.5

A lightweight, offline-first Android tracker for The Whole Truth protein bars.

## Install

1. Open the repo's **Releases** page and download `Barbook-v….apk` from the latest release.
2. Open the file on your phone and allow installs from your browser if Android asks.

Every release is signed with the same key, so a new version installs **over** the old one and keeps your ratings.

> If Android says *"App not installed as package conflicts with an existing package"*, the installed copy was signed with a different key (every build before v1.5 used a random one). Export your ratings if you can, uninstall once, then install. This only has to happen once.

## Product behaviour

- Opens directly on **All bars**; bottom navigation is only **All bars** and **Tried**.
- **Settings** (sliders icon, top right) has the theme (**Light**, **Dark** or **System**, which follows the phone) and **Export / Import ratings**.
- A compact **Unique flavours** switch shows one entry per flavour: the variant with the highest protein per 100 kcal (the one that tops the default sort). A tried status or rating on any variant carries over to that entry. All bars only.
- Sorting: protein per 100 kcal (default, high to low) and ₹ per 20g protein (low to high).
- Marketplace price follows the selected filter; Any shows the lower price and where it is from.
- Personal data is a tried/not-tried status and an optional rating from 1 to 10. Ratings 8–10 are green, 6–7 yellow, 1–5 red.
- Personal data is stored only on the phone (`localStorage`, key `barbook-v1-personal-edits`). No cloud sync, accounts, analytics or uploads.

## Backing up your ratings

Uninstalling the app or clearing its data erases your ratings. In **Settings → Backup**:

- **Export** saves `barbook-backup-YYYY-MM-DD.json` wherever you choose (Files, Drive, …).
- **Import** replaces the ratings on the phone with a backup file, after asking you to confirm. Invalid files are rejected and never change your data.

## Project structure

- `app/src/main/assets/index.html` — the whole app UI and product data (single source of truth).
- `app/src/main/java/com/barbook/wholetruth/MainActivity.java` — Android WebView wrapper, including the file bridge for export/import.
- `app/src/main/res/` — launcher icon and styles.
- `signing/barbook.keystore` — fixed signing key (see below).
- `scripts/validate_barbook.py` — regression checks run by CI.
- `.github/workflows/build-apk.yml` — validates and builds a signed APK on every push and pull request.
- `.github/workflows/release.yml` — publishes a GitHub release when the version changes.
- `.github/copilot-instructions.md`, `.github/prompts/` — rules for Copilot or any coding agent.

## Releasing

1. Change `versionCode` and `versionName` in `app/build.gradle` and `APP_VERSION` in `index.html` (the validator checks they match).
2. Merge to `main`.
3. The **Release Barbook** workflow builds the signed APK and creates the release `v<versionName>` with the APK and a source zip attached. If that version already has a release, it does nothing.

To rebuild the current version by hand, open **Actions → Release Barbook → Run workflow**.

## Signing

All builds (debug and release) use `signing/barbook.keystore`, so APKs from different builds can update each other. The key is committed on purpose because this is a personal sideloaded app, not a Play Store app. The trade-off: anyone who copies the key could build an APK your phone accepts as an update, but they would still have to get you to install it.

To keep the key private, add these GitHub Actions secrets and the build will use them instead of the committed key: `BARBOOK_KEYSTORE` (path), `BARBOOK_KEYSTORE_PASSWORD`, `BARBOOK_KEY_ALIAS`, `BARBOOK_KEY_PASSWORD`. Switching to a different key means everyone must uninstall once.

## Working with Copilot

Use the GitHub Copilot coding agent on this repository: describe a change, let it open a pull request, then review and merge. Copilot follows `.github/copilot-instructions.md` and CI runs `python scripts/validate_barbook.py` plus a signed build on the pull request. The project zip is only an optional backup; you never upload it anywhere.

## Local checks

```
python scripts/validate_barbook.py
gradle :app:assembleRelease     # needs the Android SDK
```

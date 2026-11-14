# Barbook repository instructions

- Treat this as an existing Android WebView app, not a greenfield rebuild.
- Canonical UI source: `app/src/main/assets/index.html`. Do not add a second root-level `index.html` or nested project folders.
- Preserve the Android application ID `com.barbook.wholetruth`.
- Preserve `localStorage` key `barbook-v1-personal-edits`; never rename or clear it without a migration and an explicit user-approved backup plan.
- Personal data must remain on-device. Do not add cloud sync, accounts, remote databases, analytics, or tracking. The only way data leaves the phone is the user's own Export in Settings.
- The only personal tasting fields are `tried` (boolean) and `rating` (nullable integer 1–10). Do not add free-text tasting notes. Backup files must hold only those fields and be sanitised on import.
- Catalogue sorting must contain exactly two options: protein per 100 kcal (default, descending) and ₹ per 20g protein (ascending). Do not reintroduce raw price, raw calories, or raw protein sorting.
- Marketplace price display must follow the selected marketplace filter. In Any, show the lower available price and identify its source.
- Navigation: open directly to All bars; bottom navigation is only All bars and Tried. Settings opens from the header icon as a sheet. Do not reintroduce Home or an inert header search shortcut. Remove redundant tracker-sheet footer notes.
- Keep light/dark mode, Save/Discard editing, the compact Unique flavours switch, and Settings export/import working.
- Rating colours: 8–10 green, 6–7 yellow, 1–5 red.
- Rendering rule (prevents screen flashing): build the page shell once, then update only what changed. Never replace an open sheet or re-render the whole page for an ordinary tap. Entrance animations belong only on the `.enter` class used when a sheet first opens. Support `prefers-reduced-motion`; keep motion understated.
- Keep the product catalogue data unchanged unless the task explicitly requests a data correction.
- Keep the repository minimal. Android launcher assets under `app/src/main/res` are required; remove only files proven unused.
- Signing: all builds use the fixed key `signing/barbook.keystore` so releases install over each other. Do not replace it or change the signing configuration without explicit owner approval; doing so forces every install to be removed once. Build the signed release APK (`:app:assembleRelease`), never a debug APK for distribution.
- For every feature, add or update checks in `scripts/validate_barbook.py`, run it, and describe changed files and any manual acceptance test.
- Increment `versionCode` and `versionName` in `app/build.gradle` (and `APP_VERSION` in `index.html`) for a user-facing release. Merging that change to `main` publishes the release automatically.
- Open pull requests for changes; do not merge them without the repository owner's approval.

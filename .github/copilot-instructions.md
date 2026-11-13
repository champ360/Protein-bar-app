# Barbook repository instructions

- Treat this as an existing Android WebView app, not a greenfield rebuild.
- Canonical UI source: `app/src/main/assets/index.html`. Do not add a second root-level `index.html`.
- Preserve the Android application ID `com.barbook.wholetruth`.
- Preserve `localStorage` key `barbook-v1-personal-edits`; never rename or clear it without a migration and an explicit user-approved backup plan.
- Personal data must remain on-device. Do not add cloud sync, accounts, remote databases, analytics, or tracking.
- The only personal tasting fields are `tried` (boolean) and `rating` (nullable integer 1–10). Do not add free-text tasting notes.
- Catalogue sorting must contain exactly two options: protein per 100 kcal (default, descending) and ₹ per 20g protein (ascending). Do not reintroduce raw price, raw calories, or raw protein sorting.
- Marketplace price display must follow the selected marketplace filter. In Any, show the lower available price and identify its source.
- Keep light/dark mode, Save/Discard editing, and the compact Unique flavours switch working. Open directly to All bars; do not reintroduce Home or the inert header search shortcut. Keep only All bars and Tried in bottom navigation. Remove redundant tracker-sheet footer notes.
- Prefer understated, smooth transitions; avoid bouncy/snappy motion and support `prefers-reduced-motion`. Rating colors: 8–10 green, 6–7 yellow, 1–5 red.
- Keep the product catalogue data unchanged unless the task explicitly requests a data correction.
- Keep the repository minimal. Android launcher assets under `app/src/main/res` are required; remove only files proven unused.
- For every feature, add or update appropriate checks, build the APK, and describe changed files and any manual acceptance test.
- Increment `versionCode` and `versionName` for a user-facing APK release. Do not change the signing identity or introduce a new signing key without explicit review.
- Do not merge pull requests or publish a release without the repository owner's approval.

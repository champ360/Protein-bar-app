---
name: Barbook feature change
description: Implement a Barbook improvement in a safe, reviewable pull request.
---

Implement the following Barbook change in this existing project: ${input:change:Describe the requested change}

Before editing, read `.github/copilot-instructions.md` and `README.md`. Preserve the current product data, localStorage key, Android application ID, signing key, existing tried/rating data, light/dark mode, unique-flavours toggle, Settings export/import, and the two approved sort modes unless the request explicitly says otherwise. Do not add cloud sync, accounts, analytics, free-text tasting notes, or additional raw size-biased sorts. Do not re-render the whole page or replay sheet animations on ordinary taps.

Make the smallest cohesive change. Add or update checks, run `python scripts/validate_barbook.py`, and build with `gradle --no-daemon :app:assembleRelease` when the Android SDK is available. Open a pull request describing changed files, tests, and any manual phone checks. Never merge the PR, change the signing key, delete or migrate user data, or bump the release version without explicit owner approval.

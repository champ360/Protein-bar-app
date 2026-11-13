---
name: Barbook feature change
description: Implement a Barbook improvement in a safe, reviewable pull request.
---

Implement the following Barbook change in this existing project: ${input:change:Describe the requested change}

Before editing, read `.github/copilot-instructions.md` and `README.md`. Preserve the current product data, localStorage key, Android application ID, existing tried/rating data, light/dark mode, unique-flavours toggle, and the two approved sort modes unless the request explicitly says otherwise. Do not add cloud sync, accounts, analytics, free-text tasting notes, or additional raw size-biased sorts.

Make the smallest cohesive change. Add or update checks, run `python scripts/validate_barbook.py`, and build with `gradle --no-daemon :app:assembleDebug` when the Android SDK is available. Open a pull request describing changed files, tests, and any manual phone checks. Never merge the PR, change signing identity, delete/migrate user data, or publish a release without explicit owner approval.

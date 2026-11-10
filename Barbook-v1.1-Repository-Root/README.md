# Barbook — The Whole Truth protein bar tracker

A small, offline-first Android app for browsing the 23 flavours in the supplied tracker, comparing nutrition and prices, and keeping a personal tasting log.

## What's inside

- `app/src/main/assets/index.html` — the responsive app UI and tracker data
- `app/src/main/java/com/barbook/wholetruth/MainActivity.java` — a lightweight Android WebView wrapper with dark/light system-bar support
- `.github/workflows/build-apk.yml` — a GitHub Actions workflow that builds an installable debug APK

## Features

- Sort by protein amount, protein per 100 kcal, cost per 20g protein, website price, calories, or rating
- Cost sorting uses the cheapest provider available under the selected availability filter
- Side-by-side Blinkit and website prices, including cost per 20g protein
- Dark and light modes, remembered on the device
- Tasting-log changes use a draft editor with explicit **Save changes** and **Discard** actions
- Unsaved edits trigger a discard confirmation before the detail sheet can close
- Search, series filters, availability filters, and a personal tasting list
- Offline-first storage; no account or network connection is required for normal use

## Build an APK with GitHub Actions

This project is configured to build on GitHub's Android-capable runner.

1. Create a new GitHub repository and upload the contents of this folder (the files inside `barbook-android`, not the outer folder).
2. Open the repository's **Actions** tab and select **Build Barbook APK**.
3. Choose **Run workflow**. The workflow compiles the Android project and publishes an artifact named `barbook-debug-apk`.
4. Open that workflow run, download the artifact, and extract `app-debug.apk`.
5. Send `app-debug.apk` to your Android phone and install it. Android may ask you to allow installs from the app you used to open the APK.

The debug APK is signed for direct testing and installation. It is not a Play Store release build.

## Preview the web app

Open `index.html` in a browser. The same page is bundled into the Android app.

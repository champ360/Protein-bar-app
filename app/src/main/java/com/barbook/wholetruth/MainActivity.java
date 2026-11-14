package com.barbook.wholetruth;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.drawable.ColorDrawable;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

public class MainActivity extends Activity {
    private static final int REQUEST_EXPORT = 4101;
    private static final int REQUEST_IMPORT = 4102;
    private static final int MAX_BACKUP_BYTES = 1000000;
    private static final String PREFS = "barbook";
    private static final String PREF_DARK = "dark";

    private WebView webView;
    private String pendingExport;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        // Start in the theme the user last chose, so a dark-mode user never sees a light flash
        // while the page is still loading. The page confirms the theme once it is running.
        boolean dark = getSharedPreferences(PREFS, MODE_PRIVATE).getBoolean(PREF_DARK, false);

        webView = new WebView(this);
        updateSystemBars(dark);
        webView.setOverScrollMode(View.OVER_SCROLL_NEVER);
        webView.setVerticalScrollBarEnabled(false);

        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setDatabaseEnabled(true);
        settings.setDefaultTextEncodingName("UTF-8");

        webView.addJavascriptInterface(new NativeBridge(), "BarbookNative");
        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient());
        setContentView(webView);
        webView.loadUrl("file:///android_asset/index.html");
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Coming back from recents: repaint the window and WebView in the saved theme straight away.
        updateSystemBars(getSharedPreferences(PREFS, MODE_PRIVATE).getBoolean(PREF_DARK, false));
    }

    private void updateSystemBars(boolean dark) {
        int barColor = dark ? Color.rgb(21, 20, 27) : Color.rgb(247, 246, 242);
        getWindow().setBackgroundDrawable(new ColorDrawable(barColor));
        getWindow().setStatusBarColor(barColor);
        getWindow().setNavigationBarColor(barColor);
        int flags = dark ? 0 : (View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        getWindow().getDecorView().setSystemUiVisibility(flags);
        if (webView != null) webView.setBackgroundColor(barColor);
    }

    /** Runs a JavaScript call on the page. Must be called on the UI thread. */
    private void callJs(String script) {
        if (webView != null) webView.evaluateJavascript(script, null);
    }

    /** Methods exposed to the page as window.BarbookNative. They run on a background thread. */
    private final class NativeBridge {
        @JavascriptInterface
        public void setTheme(boolean dark) {
            getSharedPreferences(PREFS, MODE_PRIVATE).edit().putBoolean(PREF_DARK, dark).apply();
            runOnUiThread(() -> updateSystemBars(dark));
        }

        @JavascriptInterface
        public void saveBackup(String fileName, String json) {
            runOnUiThread(() -> {
                pendingExport = json;
                Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("application/json");
                intent.putExtra(Intent.EXTRA_TITLE, fileName);
                try {
                    startActivityForResult(intent, REQUEST_EXPORT);
                } catch (ActivityNotFoundException e) {
                    pendingExport = null;
                    callJs("onBackupError(" + JSONObject.quote("No file manager is available on this phone.") + ")");
                }
            });
        }

        @JavascriptInterface
        public void pickBackup() {
            runOnUiThread(() -> {
                Intent intent = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("*/*");
                try {
                    startActivityForResult(intent, REQUEST_IMPORT);
                } catch (ActivityNotFoundException e) {
                    callJs("onBackupError(" + JSONObject.quote("No file manager is available on this phone.") + ")");
                }
            });
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_EXPORT) {
            String json = pendingExport;
            pendingExport = null;
            Uri uri = (resultCode == RESULT_OK && data != null) ? data.getData() : null;
            if (uri == null || json == null) {
                callJs("onBackupSaved(false)");
                return;
            }
            try (OutputStream out = getContentResolver().openOutputStream(uri, "wt")) {
                if (out == null) throw new IOException("No output stream");
                out.write(json.getBytes(StandardCharsets.UTF_8));
                out.flush();
                callJs("onBackupSaved(true)");
            } catch (IOException | RuntimeException e) {
                callJs("onBackupError(" + JSONObject.quote("Could not save the backup file.") + ")");
            }
        } else if (requestCode == REQUEST_IMPORT) {
            Uri uri = (resultCode == RESULT_OK && data != null) ? data.getData() : null;
            if (uri == null) return;
            try (InputStream in = getContentResolver().openInputStream(uri)) {
                if (in == null) throw new IOException("No input stream");
                ByteArrayOutputStream buffer = new ByteArrayOutputStream();
                byte[] chunk = new byte[8192];
                int read;
                while ((read = in.read(chunk)) != -1) {
                    buffer.write(chunk, 0, read);
                    if (buffer.size() > MAX_BACKUP_BYTES) {
                        callJs("onBackupError(" + JSONObject.quote("That file is too large to be a Barbook backup.") + ")");
                        return;
                    }
                }
                String text = new String(buffer.toByteArray(), StandardCharsets.UTF_8);
                callJs("onBackupPicked(" + JSONObject.quote(text) + ")");
            } catch (IOException | RuntimeException e) {
                callJs("onBackupError(" + JSONObject.quote("Could not read that file.") + ")");
            }
        }
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        if (webView == null) {
            super.onBackPressed();
            return;
        }
        webView.evaluateJavascript("handleBackPressed()", value -> {
            if ("true".equals(value)) {
                return;
            }
            if (webView.canGoBack()) {
                webView.goBack();
            } else {
                super.onBackPressed();
            }
        });
    }
}

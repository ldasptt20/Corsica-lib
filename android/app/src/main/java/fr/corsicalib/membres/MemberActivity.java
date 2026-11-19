package fr.corsicalib.membres;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.widget.Toast;

/** Private companion for the member server connected through adb reverse. */
public final class MemberActivity extends Activity {
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        setContentView(R.layout.start);
        findViewById(R.id.signup).setOnClickListener(view -> openMemberPage("/inscription/"));
        findViewById(R.id.login).setOnClickListener(view -> openMemberPage("/connexion/"));
    }

    private void openMemberPage(String path) {
        Uri page = Uri.parse("http://127.0.0.1:8000" + path);
        Intent browser = new Intent(Intent.ACTION_VIEW, page);
        // The Custom Tabs protocol accepts a null session for a standalone launch.
        Bundle extras = new Bundle();
        extras.putBinder("android.support.customtabs.extra.SESSION", null);
        browser.putExtras(extras);
        try {
            startActivity(browser);
        } catch (ActivityNotFoundException unavailable) {
            Toast.makeText(this, R.string.missing_browser, Toast.LENGTH_LONG).show();
        }
    }
}

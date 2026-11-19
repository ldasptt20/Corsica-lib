package fr.corsicalib.membres;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.net.Uri;
import android.os.Bundle;
import android.widget.TextView;
import androidx.browser.customtabs.CustomTabsIntent;

/** Private Android client for the member server forwarded with adb reverse. */
public final class MemberActivity extends Activity {
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        Uri account = Uri.parse("http://127.0.0.1:8000/compte/");
        try {
            new CustomTabsIntent.Builder().build().launchUrl(this, account);
            finish();
        } catch (ActivityNotFoundException unavailable) {
            TextView message = new TextView(this);
            message.setText("Un navigateur Android est nécessaire pour ouvrir Corsica Lib.");
            setContentView(message);
        }
    }
}

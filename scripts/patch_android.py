"""Patches the generated Capacitor Android project: landscape, fullscreen, keep screen on."""
import re, pathlib

root = pathlib.Path("android/app/src/main")

# 1) Landscape orientation
mf = root / "AndroidManifest.xml"
t = mf.read_text()
if "screenOrientation" not in t:
    t = t.replace("<activity", '<activity\n            android:screenOrientation="sensorLandscape"', 1)
mf.write_text(t)

# 2) Fullscreen + display cutout support in theme
st = root / "res/values/styles.xml"
t = st.read_text()
extra = (
    '        <item name="android:windowFullscreen">true</item>\n'
    '        <item name="android:windowLayoutInDisplayCutoutMode">shortEdges</item>\n'
)
if "windowFullscreen" not in t:
    t = t.replace('<style name="AppTheme.NoActionBar" parent="Theme.AppCompat.DayNight.NoActionBar">',
                  '<style name="AppTheme.NoActionBar" parent="Theme.AppCompat.DayNight.NoActionBar">\n' + extra, 1)
st.write_text(t)

# 3) Immersive MainActivity
java = next(root.glob("java/**/MainActivity.java"))
java.write_text('''package com.birdblast.game;

import android.os.Bundle;
import android.view.WindowManager;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        goImmersive();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) goImmersive();
    }

    private void goImmersive() {
        WindowCompat.setDecorFitsSystemWindows(getWindow(), false);
        WindowInsetsControllerCompat c =
            WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView());
        c.hide(WindowInsetsCompat.Type.systemBars());
        c.setSystemBarsBehavior(WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
    }
}
''')
print("Patched:", mf, st, java)

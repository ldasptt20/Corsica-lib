package fr.corsicalib.membres;

import android.app.*;
import android.os.Bundle;
import android.content.Intent;
import android.net.Uri;
import android.view.View;
import android.graphics.Color;
import android.widget.*;
import org.json.*;
import java.util.*;
import java.util.concurrent.*;

public final class MemberActivity extends Activity {
    private final MemberApi api = new MemberApi();
    private final ExecutorService worker = Executors.newSingleThreadExecutor();
    private LinearLayout panel;
    private TextView status;
    private JSONObject account;
    private final Map<String,EditText> fields = new LinkedHashMap<>();
    private int generation;
    private boolean busy;
    private Runnable back;
    private static final int PINK = Color.rgb(245,0,126);
    private static final int BACKGROUND = Color.rgb(12,12,15);
    private static final int SURFACE = Color.rgb(31,29,35);

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        home();
    }
    @Override public void onDestroy() { worker.shutdownNow(); super.onDestroy(); }
    @Override public void onBackPressed() { if (back == null) super.onBackPressed(); else back.run(); }
    int dp(int n) { return Math.round(n * getResources().getDisplayMetrics().density); }
    void page(String title, Runnable parent) {
        generation++;
        busy = false;
        back = parent;
        fields.clear();
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackgroundColor(BACKGROUND);
        panel = new LinearLayout(this);
        panel.setOrientation(LinearLayout.VERTICAL);
        panel.setPadding(dp(24),dp(28),dp(24),dp(28));
        scroll.addView(panel);
        setContentView(scroll);
        scroll.setOnApplyWindowInsetsListener((v,i) -> {
            v.setPadding(0,i.getSystemWindowInsetTop(),0,i.getSystemWindowInsetBottom());
            return i.consumeSystemWindowInsets();
        });
        TextView brand = label("Corsica Lib",23);
        brand.setTypeface(null,android.graphics.Typeface.BOLD_ITALIC);
        brand.setTextColor(PINK);
        brand.setGravity(android.view.Gravity.CENTER_HORIZONTAL);
        brand.setPadding(0,dp(12),0,dp(26));
        TextView heading = label(title,27);
        heading.setTypeface(null,android.graphics.Typeface.BOLD);
        heading.setPadding(0,0,0,dp(20));
        status = label("",16);
        status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
    }
    TextView label(String text,int size) {
        TextView t = new TextView(this);
        t.setText(text); t.setTextSize(size); t.setTextColor(Color.WHITE);
        t.setPadding(0,dp(7),0,dp(7));
        panel.addView(t); return t;
    }
    void button(String text, Runnable action) {
        Button b = new Button(this);
        b.setText(text); b.setAllCaps(false);
        b.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PINK));
        b.setTextColor(Color.WHITE);
        b.setTypeface(null,android.graphics.Typeface.BOLD);
        b.setMinHeight(dp(52));
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(-1,dp(56));
        lp.setMargins(0,dp(8),0,dp(8));
        panel.addView(b,lp); b.setOnClickListener(v -> { if (!busy) action.run(); });
    }
    void field(String key,String title,String value,int type) {
        label(title,14);
        EditText edit = new EditText(this); edit.setInputType(type); edit.setText(value);
        edit.setContentDescription(title);
        edit.setTextColor(Color.WHITE);
        edit.setHintTextColor(Color.LTGRAY);
        edit.setBackgroundTintList(android.content.res.ColorStateList.valueOf(PINK));
        edit.setSingleLine(type != 131073);
        panel.addView(edit); fields.put(key,edit);
    }
    Spinner kind(String initial) {
        label("Type de profil",14);
        Spinner s = new Spinner(this);
        s.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,new String[]{"Solo","Couple"}));
        s.setSelection("couple".equals(initial)?1:0); panel.addView(s); return s;
    }
    Map<String,String> values() {
        Map<String,String> data = new HashMap<>();
        for (String k:fields.keySet()) data.put(k,fields.get(k).getText().toString());
        return data;
    }
    interface Done { void accept(JSONObject data) throws Exception; }
    void request(String path,Map<String,String> form, Done done) {
        busy = true; status.setText("Connexion en cours…");
        final int screen = generation;
        worker.execute(() -> {
            try {
                JSONObject data = api.call(path,form);
                runOnUiThread(() -> {
                    if (screen != generation || isDestroyed()) return;
                    busy=false; status.setText("");
                    try { done.accept(data); } catch (Exception e) { status.setText("Impossible d’afficher le résultat."); }
                });
            } catch (Exception e) {
                runOnUiThread(() -> {
                    if (screen != generation || isDestroyed()) return;
                    busy=false; status.setText(e instanceof java.io.IOException && !(e instanceof java.net.SocketException)
                        && !(e instanceof java.net.UnknownHostException) ? e.getLocalizedMessage() : "Serveur membre inaccessible. Vérifiez la connexion.");
                });
            }
        });
    }
    void home() {
        page("Rencontres, échanges et libertés entre adultes en Corse",null);
        TextView welcome = label("ESPACE MEMBRE  ·  18+",14);
        welcome.setTextColor(PINK);
        welcome.setGravity(android.view.Gravity.CENTER_HORIZONTAL);
        welcome.setPadding(0,dp(12),0,dp(25));
        if (BuildConfig.ORIGIN.startsWith("http://127.0.0.1:"))
            label("Version de test · Les comptes nécessitent une liaison USB avec le serveur membre.",16);
        button("Se connecter",() -> credentials(false));
        button("S’inscrire",() -> credentials(true));
        TextView adultNotice = label("Réservé aux personnes majeures (18 ans et plus)",13);
        adultNotice.setGravity(android.view.Gravity.CENTER_HORIZONTAL);
    }
    void credentials(boolean signup) {
        page(signup?"Créer mon compte":"Me connecter",this::home);
        field("email","Adresse e-mail","",33); field("password","Mot de passe","",129);
        if (signup) {
            field("pseudo","Pseudonyme","",1); field("birth","Date de naissance (AAAA-MM-JJ)","",1);
            field("city","Ville","",1);
        }
        Spinner selection = signup ? kind("solo") : null;
        button(signup?"Créer mon compte":"Connexion",() -> {
            Map<String,String> form = values();
            if (selection != null) form.put("kind",selection.getSelectedItemPosition()==0?"solo":"couple");
            request("account/"+(signup?"signup":"login")+"/",form,this::dashboard);
        });
    }
    void dashboard(JSONObject state) {
        account=state;
        if (!state.optBoolean("connected")) { home(); return; }
        JSONObject p=state.optJSONObject("profile");
        page("Bonjour "+p.optString("pseudo"),null);
        status.setText(state.optString("notice"));
        if (!state.optBoolean("email_ok")) {
            label("Confirmez votre adresse avec le lien reçu par e-mail.",16);
            button("Renvoyer le lien",() -> request("account/resend/",values(),this::dashboard));
            button("Actualiser",() -> request("state/",null,this::dashboard));
        } else if (!state.optBoolean("adult")) {
            label("La vérification de majorité se déroule chez Yoti. Revenez ici après le selfie.",16);
            button("Vérifier ma majorité",() -> request("account/age/",values(),d -> {
                Uri uri=Uri.parse(d.getString("url"));
                if ("https".equals(uri.getScheme()) && "age.yoti.com".equals(uri.getHost()))
                    startActivity(new Intent(Intent.ACTION_VIEW,uri));
            }));
            button("Consulter le résultat",() -> request("result/",null,this::dashboard));
        } else {
            label("Découvrir les membres",19).setTextColor(PINK);
            button("Découvrir les profils",() -> members(false));
            button("Mes favoris  ♥",() -> members(true));
            button("Mon profil et paramètres",() -> edit(p));
        }
        button("Me déconnecter",() -> request("account/logout/",values(),this::dashboard));
    }
    void edit(JSONObject p) {
        page("Mon profil",() -> dashboard(account));
        field("pseudo","Pseudonyme",p.optString("pseudo"),1);
        field("city","Ville",p.optString("city"),1);
        field("bio","Présentation",p.optString("bio"),131073);
        Spinner s=kind(p.optString("kind"));
        button("Enregistrer",() -> {
            Map<String,String> data=values(); data.put("kind",s.getSelectedItemPosition()==0?"solo":"couple");
            request("profile/",data,this::dashboard);
        });
    }
    void members(boolean favorites) {
        page(favorites?"Mes favoris":"Les membres",() -> dashboard(account));
        request("members/",null,d -> {
            JSONArray rows=d.getJSONArray("members"); int count=0;
            for (int i=0;i<rows.length();i++) {
                JSONObject p=rows.getJSONObject(i);
                if (favorites && !p.optBoolean("favorite")) continue;
                button(p.optString("pseudo")+" · "+p.optString("city"),() -> peer(p,favorites)); count++;
            }
            if (count==0) label(favorites?"Aucun favori pour le moment.":"Aucun autre membre vérifié pour le moment.",16);
        });
    }
    void peer(JSONObject p,boolean favorites) {
        page(p.optString("pseudo"),() -> members(favorites));
        label(p.optString("city")+" · "+p.optString("kind"),16); label(p.optString("bio"),16);
        String path="members/"+p.optInt("id")+"/";
        boolean fav=p.optBoolean("favorite");
        button(fav?"Retirer des favoris":"Ajouter aux favoris",() ->
            request(path+"favorite/",Collections.singletonMap("enabled",Boolean.toString(!fav)),d -> members(favorites)));
        button("Conversation",() -> chat(p,favorites));
    }
    void chat(JSONObject p,boolean favorites) {
        page("Messages · "+p.optString("pseudo"),() -> peer(p,favorites));
        String path="members/"+p.optInt("id")+"/messages/";
        request(path,null,d -> {
            JSONArray rows=d.getJSONArray("messages");
            for (int i=0;i<rows.length();i++) {
                JSONObject m=rows.getJSONObject(i);
                label((m.optBoolean("mine")?"Moi":p.optString("pseudo"))+" · "+m.optString("body"),16);
            }
            field("body","Votre message","",131073);
            button("Envoyer",() -> request(path,values(),sent -> chat(p,favorites)));
            button("Actualiser",() -> chat(p,favorites));
        });
    }
}

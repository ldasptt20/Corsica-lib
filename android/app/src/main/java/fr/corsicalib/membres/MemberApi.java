package fr.corsicalib.membres;

import org.json.JSONObject;
import java.io.*;
import java.net.*;
import java.util.*;

final class MemberApi {
    private final CookieManager cookies = new CookieManager(null, CookiePolicy.ACCEPT_ORIGINAL_SERVER);
    private String csrf = "";

    JSONObject call(String path, Map<String,String> fields) throws Exception {
        if (fields != null && csrf.isEmpty()) call("state/", null);
        URI uri = URI.create(BuildConfig.ORIGIN + "/api/mobile/" + path);
        HttpURLConnection c = (HttpURLConnection)uri.toURL().openConnection();
        try {
            c.setConnectTimeout(10000);
            c.setReadTimeout(20000);
            c.setInstanceFollowRedirects(false);
            for (Map.Entry<String,List<String>> h : cookies.get(uri, Collections.emptyMap()).entrySet())
                for (String v : h.getValue()) c.addRequestProperty(h.getKey(), v);
            if (fields != null) {
                c.setRequestMethod("POST");
                c.setDoOutput(true);
                c.setRequestProperty("Content-Type", "application/x-www-form-urlencoded;charset=UTF-8");
                c.setRequestProperty("X-CSRFToken", csrf);
                c.setRequestProperty("Origin", BuildConfig.ORIGIN);
                StringBuilder body = new StringBuilder();
                for (Map.Entry<String,String> e : fields.entrySet()) {
                    if (body.length() > 0) body.append("&");
                    body.append(URLEncoder.encode(e.getKey(),"UTF-8")).append("=").append(URLEncoder.encode(e.getValue(),"UTF-8"));
                }
                try (OutputStream out = c.getOutputStream()) { out.write(body.toString().getBytes("UTF-8")); }
            }
            int code = c.getResponseCode();
            cookies.put(uri,c.getHeaderFields());
            InputStream stream = code < 400 ? c.getInputStream() : c.getErrorStream();
            if (stream == null) throw new IOException("Serveur indisponible.");
            StringBuilder data = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(stream,"UTF-8"))) {
                String line;
                while ((line = reader.readLine()) != null) data.append(line);
            }
            JSONObject result = new JSONObject(data.toString());
            if (code >= 400) throw new IOException(result.optString("error","Erreur du serveur."));
            csrf = result.optString("csrf", csrf);
            return result;
        } finally { c.disconnect(); }
    }
}

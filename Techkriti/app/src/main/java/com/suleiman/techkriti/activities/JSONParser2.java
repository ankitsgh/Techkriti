package com.suleiman.techkriti.activities;

/**
 * Created by HP on 12/9/2015.
 */
import android.text.TextUtils;
import android.util.Log;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.net.URLEncoder;
import java.util.HashMap;

public class JSONParser2 {

    String charset = "UTF-8";
    HttpURLConnection conn;



    DataOutputStream wr;
    StringBuilder result;
    URL urlObj;
    URL urlObj1;
    JSONObject jObj = null;

    StringBuilder sbParams;
    String paramsString;
    static final String COOKIES_HEADER = "Set-Cookie";
    static java.net.CookieManager msCookieManager = new java.net.CookieManager();

    public JSONObject makeHttpRequest(String url, String method,
                                      HashMap<String, String> params, java.net.CookieManager msCookieManager1) {
        msCookieManager=msCookieManager1;
        sbParams = new StringBuilder();
        int i = 0;
        for (String key : params.keySet()) {
            try {
                if (i != 0){
                    sbParams.append("&");
                }
                sbParams.append(key).append("=")
                        .append(URLEncoder.encode(params.get(key), charset));

            } catch (UnsupportedEncodingException e) {
                e.printStackTrace();
            }
            i++;
        }

        if (method.equals("POST")) {
            // request method is POST
            try {
                urlObj = new URL(url);

                conn = (HttpURLConnection) urlObj.openConnection();

                conn.setDoOutput(true);

                conn.setRequestMethod("POST");

                conn.setRequestProperty("Accept-Charset", charset);

                conn.setReadTimeout(10000);
                conn.setConnectTimeout(15000);

                conn.connect();

                paramsString = sbParams.toString();

                wr = new DataOutputStream(conn.getOutputStream());
                wr.writeBytes(paramsString);
                wr.flush();
                wr.close();

            } catch (IOException e) {
                e.printStackTrace();
            }
        }
        else if(method.equals("GET")){
            // request method is GET

            if (sbParams.length() != 0) {
                url += "?" + sbParams.toString();
            }

            try {
                urlObj1 = new URL(url);
                conn = (HttpURLConnection) urlObj1.openConnection();

                conn.setDoOutput(false);

                conn.setRequestMethod("GET");

                conn.setRequestProperty("Accept-Charset", charset);

                conn.setConnectTimeout(15000);
                if(msCookieManager.getCookieStore().getCookies().size() > 0)
                {

                    conn.setRequestProperty("Cookie",
                            TextUtils.join(";", msCookieManager.getCookieStore().getCookies()));
                }

                conn.connect();

            } catch (IOException e) {
                e.printStackTrace();
            }

        }

        try {
            InputStream in = new BufferedInputStream(conn.getInputStream());
            BufferedReader reader = new BufferedReader(new InputStreamReader(in));
            result = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                result.append(line);
            }

            Log.d("JSON Parser", "result: " + result.toString());




        } catch (IOException e) {
            e.printStackTrace();
        }
        conn.disconnect();

        try {
            jObj = new JSONObject(result.toString());


        } catch (JSONException e) {
            Log.e("JSON Parser2", "Error parsing data " + e.toString());
        }


        return jObj;
    }

}


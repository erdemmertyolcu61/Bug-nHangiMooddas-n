package app.sinemood;

import android.webkit.WebSettings;

import com.getcapacitor.BridgeActivity;

/**
 * Android WebView, sistemdeki "Yazı tipi boyutu" ayarını web içeriğine
 * DOĞRUDAN uygular (iOS'taki WKWebView uygulamaz). Ayar %130'a çekildiğinde
 * yalnız yazılar büyür, kutular (h-12, w-10, alt menü hücreleri) sabit px
 * kaldığı için tasarım dağılır: alt menüde "MOODLAR" kelimenin ortasından
 * "MOODLA / R" diye bölünüyor, %150'de beş etiketten dördü bölünüp kırpılıyor.
 *
 * Ölçeği tamamen yok saymak (setTextZoom(100)) erişilebilirliği kırar; bu
 * yüzden tasarımın sorunsuz taşıdığı ölçüde saygı gösterilir, üstü kırpılır.
 * Sınır tarayıcıda ölçülerek bulundu: 1.15 temiz, 1.30 bölünmeye başlıyor.
 */
public class MainActivity extends BridgeActivity {

    /** Tarayıcıda doğrulanan en yüksek güvenli yazı ölçeği. */
    private static final float MAX_FONT_SCALE = 1.15f;

    @Override
    public void onStart() {
        super.onStart();
        applyTextZoomCap();
    }

    /**
     * onStart'ta çağrılır: kullanıcı uygulamayı arka plandayken sistem yazı
     * boyutunu değiştirebilir, geri döndüğünde sınır yeniden uygulanmalı.
     */
    private void applyTextZoomCap() {
        if (bridge == null || bridge.getWebView() == null) return;
        float systemScale = getResources().getConfiguration().fontScale;
        int zoom = Math.round(Math.min(systemScale, MAX_FONT_SCALE) * 100f);
        WebSettings settings = bridge.getWebView().getSettings();
        if (settings.getTextZoom() != zoom) {
            settings.setTextZoom(zoom);
        }
    }
}
